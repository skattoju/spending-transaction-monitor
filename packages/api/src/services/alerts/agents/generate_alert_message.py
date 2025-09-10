from langchain_core.tools import tool

from .utils import extract_response, get_llm_client


@tool
def generate_alert_message(
    transaction: dict, query_result: str, alert_text: str, alert_rule: dict
) -> str:
    """
    Generate a user-facing alert message based on AlertRule.

    Args:
        transaction: Transaction data
        query_result: SQL query result
        alert_text: Natural language alert description
        alert_rule: AlertRule object containing alert_type and other metadata
    """
    # Extract alert_type from the AlertRule object
    alert_type_enum = alert_rule.get('alert_type')

    # Map AlertType enum to string for backward compatibility with existing prompts
    alert_type_map = {
        'AMOUNT_THRESHOLD': 'spending',
        'LOCATION_BASED': 'location',
        'MERCHANT_CATEGORY': 'merchant',
        'MERCHANT_NAME': 'merchant',
        'PATTERN_BASED': 'pattern',
        'FREQUENCY_BASED': 'frequency',
        'CUSTOM_QUERY': 'custom',
    }

    alert_type = alert_type_map.get(str(alert_type_enum), 'general')
    first = transaction.get('first', '')
    last = transaction.get('last', '')
    user = f'{first} {last}'.strip()
    amount = transaction.get('amt')
    category = transaction.get('category', '')
    merchant = transaction.get('merchant', '')
    city = transaction.get('city', '')
    state = transaction.get('state', '')

    if alert_type == 'spending':
        prompt = f"""
The user {user} triggered an alert for excessive spending.

- Alert: "{alert_text}"
- Transaction amount: ${amount}
- Category: {category}
- Merchant: {merchant}
- SQL result: {query_result}

Write a 1-2 sentence friendly alert message explaining why the spending alert was triggered.
"""
    elif alert_type == 'location':
        prompt = f"""
The user {user} triggered an alert for a location-based transaction.

- Alert: "{alert_text}"
- Location: {city}, {state}
- Merchant: {merchant}
- SQL result: {query_result}

Write a 1-2 sentence alert message explaining why the location alert was triggered.
"""
    elif alert_type == 'merchant':
        prompt = f"""
The user {user} triggered an alert related to a new or repeated merchant.

- Alert: "{alert_text}"
- Merchant: {merchant}
- SQL result: {query_result}

Write a 1-2 sentence friendly alert message explaining why this merchant alert was triggered.
"""
    elif alert_type == 'pattern':
        prompt = f"""
The user {user} triggered a pattern-based alert for unusual spending behavior.

- Alert: "{alert_text}"
- Transaction amount: ${amount}
- Merchant: {merchant}
- SQL result: {query_result}

Write a 1-2 sentence friendly alert message explaining the unusual pattern detected.
"""
    elif alert_type == 'frequency':
        prompt = f"""
The user {user} triggered a frequency-based alert for repeated transactions.

- Alert: "{alert_text}"
- Transaction amount: ${amount}
- Merchant: {merchant}
- SQL result: {query_result}

Write a 1-2 sentence friendly alert message about the frequency pattern.
"""
    else:
        prompt = f"""
User: {user}
Alert: {alert_text}
Transaction: ${amount} at {merchant}
SQL Result: {query_result}

Write a friendly alert message for a general transaction alert.
"""

    client = get_llm_client()
    response = client.invoke(prompt)
    if hasattr(response, 'content') and response.content:
        content = response.content
    else:
        content = response
    return extract_response(content)
