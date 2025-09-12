# agents/alert_parser.py

from langchain.tools import tool

from .utils import extract_sql, get_llm_client


def build_prompt(last_transaction: dict, alert_text: str, alert_rule: dict) -> str:
    user_id = last_transaction.get('user_id', '').strip()
    transaction_date = last_transaction.get('transaction_date', '')
    merchant_name = alert_rule.get('merchant_name', '').lower()
    merchant_category = alert_rule.get('merchant_category', '').lower()

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
2. `last_txn` must ALWAYS include user_id in its SELECT list, along with transaction_date, amount, merchant_name, merchant_category, and trans_num:
   ```sql
   WITH last_txn AS (
     SELECT user_id, transaction_date, amount, merchant_name, merchant_category, trans_num
     FROM transactions
     WHERE user_id = '{user_id}'
       AND transaction_date = TIMESTAMP '{transaction_date}'
     LIMIT 1
   )
   ```
3. For aggregate comparisons (averages, thresholds, frequency counts, recurring charges):
   - CTEs like `historical` must always return a **single scalar aggregate** (e.g., AVG, SUM, COUNT).
   - Never return raw rows in aggregate CTEs.
   - Always use CROSS JOIN last_txn to bring in context.
   - Exclude the last transaction from history (`t.transaction_date < lt.transaction_date`).
   - Always wrap the final SELECT in a CASE ... ELSE so it returns exactly one row:
     ```sql
    historical AS (
      SELECT COALESCE(AVG(t.amount),0) AS avg_amount
      FROM transactions t
      CROSS JOIN last_txn lt
      WHERE t.user_id = lt.user_id
        AND t.merchant_category = lt.merchant_category
        AND t.transaction_date >= lt.transaction_date - INTERVAL '30 days'
        AND t.transaction_date < lt.transaction_date
    )
    SELECT CASE
      WHEN lt.amount > h.avg_amount * 1.4
        THEN 'ALERT: Dining expense exceeds 30-day average by >40%'
      ELSE 'NO_ALERT'
    END AS alert
    FROM last_txn lt
    CROSS JOIN historical h;
     ```
   - This ensures only one row is returned and avoids GROUPING errors.
4. When comparing last transaction against history:
   - EXCLUDE the last transaction (t.transaction_date < lt.transaction_date).

5. Time-window alerts:
   - Anchor to last_transaction.transaction_date = '{transaction_date}'.
   - Use BETWEEN (TIMESTAMP '{transaction_date}' - INTERVAL 'X') AND TIMESTAMP '{transaction_date}'.
   - Always cast literals to TIMESTAMP before subtracting intervals.
6. Recurring charge alerts:
   - A "new recurring charge pattern" means:
     a) The last transaction’s merchant/category has **no prior history before (last_transaction_date - 60 days)**.
     b) The same merchant/category appears **at least twice** within the last 60 days (including the last transaction).
   - Use two CTEs:
     - `prior_txns`: transactions before (last_transaction_date - INTERVAL '60 days').
     - `recent_txns`: count of this merchant/category in the last 60 days including last_transaction_date.
   - Final SELECT should return an alert only when NOT EXISTS prior_txns AND recent_txns.count > 1.
7. Thresholds:
   - "$20 more" → last_txn.amount > COALESCE(h.avg_amount,0) + 20.
   - "20% more" → last_txn.amount > COALESCE(h.avg_amount,0) * 1.2.
8. Ratios:
   - Never divide by columns directly.
   - Rewrite as multiplication and ensure previous_amount IS NOT NULL.
9. Window functions:
   - If using LAG/LEAD, do not mix with GROUP BY.
10. If GROUP BY is required:
   - Must include transactions.user_id.
   - All non-aggregated SELECT columns must be in GROUP BY.
11. Derived columns:
   - Do not use them directly in WHERE.
   - Wrap in a subquery or CTE, then filter in the outer query.
12. In the outer SELECT, never reference table aliases from inside a CTE.
13. For exponentiation, always use POWER(x,2).
14. Valid alerts: transaction amount, transaction_date, merchant info, location, or user profile.
15. If unrelated (weather, sports, etc.), return exactly "NOT_APPLICABLE".
16. Geospatial distance:
   - If PostGIS is available:
     ```sql
     ST_Distance(
       ST_SetSRID(ST_MakePoint(lon1, lat1), 4326)::geography,
       ST_SetSRID(ST_MakePoint(lon2, lat2), 4326)::geography
     ) / 1000
     ```
   - If PostGIS is not available: use Haversine formula in pure SQL:
     ```sql
     6371 * acos(
       cos(radians(lat1)) * cos(radians(lat2)) *
       cos(radians(lon2) - radians(lon1)) +
       sin(radians(lat1)) * sin(radians(lat2))
     )
     ```
   - Always return kilometers.
17. Use only columns listed in schema.
18. CTE and table aliases must be valid identifiers in snake_case.
19. If the alert involves a merchant name or category, use the following:
   - merchant_name: {merchant_name}
   - merchant_category: {merchant_category}
20. Always fully qualify columns inside aggregates (e.g., t.amount).
21. Wrap aggregates in COALESCE with safe defaults to prevent NULL issues.
22. Normalize merchant_name and merchant_category with LOWER() in all comparisons.
23. For **same-merchant same-day alerts**:
   - You MUST join `transactions t` with `last_txn lt ON t.user_id = lt.user_id`.
   - Compare using `t.merchant_name = lt.merchant_name` AND `t.transaction_date::date = lt.transaction_date::date`.
   - Never reference `last_txn` columns directly without a join.

---

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
def parse_alert_to_sql_with_context(
    transaction: dict, alert_text: str, alert_rule: dict
) -> str:
    """
    Inputs: { "transaction": {dict}, "alert_text": str, "alert_rule": dict }
    Returns: SQL query
    """
    client = get_llm_client()
    prompt = build_prompt(transaction, alert_text, alert_rule)
    response = client.invoke(prompt)

    return extract_sql(str(response))
