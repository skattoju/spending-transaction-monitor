# agents/alert_parser.py

from langchain.tools import tool

from .utils import extract_sql, get_llm_client


def build_prompt(last_transaction: dict, alert_text: str) -> str:
    user_id = last_transaction.get('user_id', '').strip()
    _ = last_transaction.get('first_name', '').strip()
    _ = last_transaction.get('last_name', '').strip()
    transaction_date = last_transaction.get('transaction_date', '')
    _ = last_transaction.get('trans_num', '')

    schema = """
Table: transactions
Columns:
- id: primary key
- user_id : reference id of the user in the users table
- transaction_date: DateTime
- credit_card_num: text
- amount: float
- currency: text
- description: text
- merchant_name: text
- merchant_category: text
- merchant_city: text
- merchant_state: text
- merchant_country: text
- merchant_latitude: float
- merchant_longitude: float
- merchant_zipcode: text
- trans_num: text
- authorization_code: text

Table: users
Columns:
- id: text
- first_name: text
- last_name: text
- email: text
- phone_number: text
- address_street: text
- address_city: text
- address_state: text
- address_country: text 
- address_zipcode: integer
- last_app_location_latitude   float
- last_app_location_longitude  float
- last_app_location_timestamp  DateTime
- last_transaction_latitude   float
- last_merchant_longitude  float
- last_transaction_timestamp  DateTime
- last_merchant_city       text
- last_merchant_state      text
- last_merchant_country    text
"""

    prompt = f"""
You are a SQL assistant.
You must generate **PostgreSQL-compatible SQL** only.

❗ HARD RULES:
1. Always filter by the current user: transactions.user_id = '{user_id}'.
2. When the alert involves a **count or frequency of transactions** 
   (e.g., "more than 5 transactions in the last hour"):
   - The count must INCLUDE the last transaction itself.
   - Use a CTE to compute the count over the time window, then CROSS JOIN with the last transaction row for context.
3. When the alert compares the **last transaction’s value** (amount, merchant, etc.) against history:
   - EXCLUDE the last transaction from the historical aggregate by filtering with transaction_date < '{transaction_date}'.
   - Only compare the last transaction against that aggregate.
4. Time-window alerts:
   - Anchor to last_transaction.transaction_date = '{transaction_date}'.
   - Use BETWEEN (TIMESTAMP '{transaction_date}' - INTERVAL 'X') AND TIMESTAMP '{transaction_date}'.
   - Always cast literals to TIMESTAMP before subtracting intervals.
5. Thresholds:
   - Dollar phrasing ("$20 more") → current_amount > avg_amount + 20.
   - Percentage phrasing ("20% more") → current_amount > avg_amount * 1.2.
6. Ratios:
   - Never divide by columns.
   - Rewrite as multiplication and ensure previous_amount IS NOT NULL.
7. Window functions:
   - If using LAG/LEAD, do not mix with GROUP BY.
8. If GROUP BY is required:
   - Must include transactions.user_id.
   - All non-aggregated SELECT columns must be in GROUP BY.
9. Derived columns (aliases like distance, avg_amount):
   - Do not use them directly in WHERE.
   - If filtering is needed, wrap the SELECT in a subquery or CTE, then filter in the outer query.
10. In the outer SELECT, never reference table aliases from inside a CTE.
    - Only use the column names defined in the CTE’s SELECT list.
11. For exponentiation, always use POWER(x,2).
12. Valid alerts involve: transaction amount, transaction_date, merchant info, location, or user profile.
13. If unrelated to transactions/users (e.g., weather, sports), return exactly "NOT_APPLICABLE".
14. Geospatial distance:
    - Preferred (if PostGIS is available): 
        ST_Distance(
            ST_SetSRID(ST_MakePoint(lon1, lat1), 4326)::geography,
            ST_SetSRID(ST_MakePoint(lon2, lat2), 4326)::geography
        ) / 1000
    - Fallback if PostGIS is not available: use Haversine formula.
    - Always return kilometers.
15. Only use columns that exist in the provided schema.
16. CTE and table aliases must be valid identifiers in snake_case (e.g., last_txn).

last_transaction Input:
{last_transaction}

Schema:
{schema}

Natural language alert: "{alert_text}"

Generate a valid SQL query that evaluates the alert.
SQL:
"""
    return prompt


@tool
def parse_alert_to_sql_with_context(transaction: dict, alert_text: str) -> str:
    """
    Inputs: { "transaction": {dict}, "alert_text": str }
    Returns: SQL query
    """
    client = get_llm_client()
    prompt = build_prompt(transaction, alert_text)
    response = client.invoke(prompt)

    return extract_sql(str(response))
