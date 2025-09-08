import uuid

from db.models import AlertRule, AlertType

# Now import everything
from langchain_core.tools import tool

from .utils import extract_response, get_llm_client


@tool
def create_alert_rule(alert_text: str, user_id: str) -> AlertRule:
    """
    Creates an AlertRule by classifying the alert text and generating a complete AlertRule object.

    Args:
        alert_text: Natural language description of the alert
        user_id: ID of the user this alert rule belongs to

    Returns:
        AlertRule: A complete AlertRule object with classified type and metadata
    """
    print('**** in create alert rule ***')
    prompt = f"""
Classify the following alert into one of the following types:
- spending: For alerts about spending amounts, thresholds, or financial limits
- location: For alerts about geographic locations or unusual location patterns
- merchant: For alerts about specific merchants or merchant categories
- pattern: For complex pattern-based or behavioral alerts

Alert: "{alert_text}"

Respond with only one word: spending, location, merchant, or pattern.
"""
    client = get_llm_client()
    response = client.invoke(prompt)
    classification = extract_response(response.content).strip().lower()

    # Map natural language classification to AlertType enum
    classification_map = {
        'spending': AlertType.AMOUNT_THRESHOLD,
        'location': AlertType.LOCATION_BASED,
        'merchant': AlertType.MERCHANT_CATEGORY,
        'pattern': AlertType.PATTERN_BASED,
    }

    # Get the classified alert type, defaulting to PATTERN_BASED for unknown classifications
    alert_type = classification_map.get(classification, AlertType.PATTERN_BASED)

    # Create and return a complete AlertRule object
    alert_rule = AlertRule(
        id=str(uuid.uuid4()),
        user_id=user_id,
        name=alert_text[:100]
        if len(alert_text) <= 100
        else alert_text[:97] + '...',  # Truncate if too long
        description=alert_text,
        is_active=True,
        alert_type=alert_type,
        natural_language_query=alert_text,
        trigger_count=0,
    )

    return alert_rule
