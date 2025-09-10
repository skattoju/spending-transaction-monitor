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
2. When the alert involves **counts or frequency** (e.g., "more than 5 transactions in the last hour"):
   - The count must INCLUDE the last transaction.
   - Use a CTE to select the last transaction (`last_txn`).
   - In the frequency CTE, always `JOIN last_txn lt ON t.user_id = lt.user_id`.
   - Reference `lt.transaction_date` safely, never `last_txn.transaction_date` directly.
   - Example:
     ```sql
     recent_txns AS (
       SELECT COUNT(*) AS txn_count
       FROM transactions t
       JOIN last_txn lt ON t.user_id = lt.user_id
       WHERE t.transaction_date BETWEEN (lt.transaction_date - INTERVAL '1 hour') AND lt.transaction_date
     )
     ```
3. When the alert compares the **last transaction** against history (amount, merchant, etc.):
   - EXCLUDE the last transaction from the historical aggregate (transaction_date < '{transaction_date}').
   - Compare the last transaction only against that aggregate.
4. Time-window alerts:
   - Anchor to last_transaction.transaction_date = '{transaction_date}'.
   - Use BETWEEN (TIMESTAMP '{transaction_date}' - INTERVAL 'X') AND TIMESTAMP '{transaction_date}'.
   - Always cast literals to TIMESTAMP before subtracting intervals.
5. Recurring charge alerts:
   - A "new recurring charge pattern" means:
     a) The last transaction’s merchant/category has **no prior history before (last_transaction_date - 60 days)**.
     b) The same merchant/category appears **at least twice** within the last 60 days (including the last transaction).
   - Use two CTEs:
     - `prior_txns`: transactions before (last_transaction_date - INTERVAL '60 days').
     - `recent_txns`: count of this merchant/category in the last 60 days including last_transaction_date.
   - Final SELECT should return an alert only when NOT EXISTS prior_txns AND recent_txns.count > 1.
6. Thresholds:
   - "$20 more" → last_txn.amount > COALESCE(AVG(t.amount),0) + 20.
   - "20% more" → last_txn.amount > COALESCE(AVG(t.amount),0) * 1.2.
7. Ratios:
   - Never divide by columns directly.
   - Rewrite as multiplication and ensure previous_amount IS NOT NULL.
8. Window functions:
   - If using LAG/LEAD, do not mix with GROUP BY.
9. If GROUP BY is required:
   - Must include transactions.user_id.
   - All non-aggregated SELECT columns must be in GROUP BY.
10. Derived columns:
   - Do not use them directly in WHERE.
   - Wrap in a subquery or CTE, then filter in the outer query.
11. In the outer SELECT, never reference table aliases from inside a CTE.
12. For exponentiation, always use POWER(x,2).
13. Valid alerts: transaction amount, transaction_date, merchant info, location, or user profile.
14. If unrelated (weather, sports, etc.), return exactly "NOT_APPLICABLE".
15. Geospatial distance:
   - If PostGIS is available, use ST_Distance with ::geography.
   - Else fallback to Haversine formula.
   - Always return kilometers.
16. Use only columns listed in schema.
17. CTE and table aliases must be valid identifiers in snake_case.
18. If the alert involves a merchant name or category, use the following:
   - merchant_name: {merchant_name}
   - merchant_category: {merchant_category}
19. Always fully qualify columns inside aggregates (e.g., t.amount).
20. Wrap aggregates in COALESCE with safe defaults to prevent NULL issues.
21. Normalize merchant_name and merchant_category with LOWER() in all comparisons.
22. For **same-merchant same-day alerts** (e.g., "charged more than once by same merchant on same day"):
   - You MUST join `transactions t` with `last_txn lt` (`JOIN last_txn lt ON t.user_id = lt.user_id`).
   - Compare using `t.merchant_name = lt.merchant_name` AND `t.transaction_date::date = lt.transaction_date::date`.
   - Never reference `last_txn` columns directly without a join.


---

📌 **EXAMPLES**

**Example 1 – Spending Threshold**
Natural language: "Alert me if my dining expense exceeds my average by more than $20 in the last 30 days."
SQL:
WITH last_txn AS (
  SELECT * FROM transactions
  WHERE user_id = '{user_id}'
  ORDER BY transaction_date DESC
  LIMIT 1
),
historical AS (
  SELECT AVG(amount) AS avg_amount
  FROM transactions t
  JOIN last_txn lt ON t.user_id = lt.user_id
  WHERE t.merchant_category = lt.merchant_category
    AND t.transaction_date < lt.transaction_date
    AND t.transaction_date >= lt.transaction_date - INTERVAL '30 days'
)
SELECT CASE
  WHEN last_txn.amount > (historical.avg_amount + 20) THEN 'ALERT'
  ELSE 'NO_ALERT'
END
FROM last_txn, historical;

**Example 2 – Frequency**
Natural language: "Alert me if I make more than 5 transactions in the last hour."
SQL:
WITH last_txn AS (
  SELECT * FROM transactions
  WHERE user_id = '{user_id}'
  ORDER BY transaction_date DESC
  LIMIT 1
),
recent_txns AS (
  SELECT COUNT(*) AS txn_count
  FROM transactions t
  JOIN last_txn lt ON t.user_id = lt.user_id
  WHERE t.transaction_date BETWEEN (lt.transaction_date - INTERVAL '1 hour') AND lt.transaction_date
)
SELECT CASE
  WHEN recent_txns.txn_count > 5 THEN 'ALERT'
  ELSE 'NO_ALERT'
END
FROM recent_txns;

**Example 3 – New Recurring Charge**
Natural language: "Alert me when a new recurring charge pattern is detected."
SQL:
WITH last_txn AS (
  SELECT * FROM transactions
  WHERE user_id = '{user_id}'
  ORDER BY transaction_date DESC
  LIMIT 1
),
prior_txns AS (
  SELECT 1 FROM transactions t
  JOIN last_txn lt ON t.user_id = lt.user_id
  WHERE t.merchant_name = lt.merchant_name
    AND t.merchant_category = lt.merchant_category
    AND t.transaction_date < (lt.transaction_date - INTERVAL '60 days')
  LIMIT 1
),
recent_txns AS (
  SELECT COUNT(*) AS count FROM transactions t
  JOIN last_txn lt ON t.user_id = lt.user_id
  WHERE t.merchant_name = lt.merchant_name
    AND t.merchant_category = lt.merchant_category
    AND t.transaction_date BETWEEN (lt.transaction_date - INTERVAL '60 days') AND lt.transaction_date
)
SELECT CASE
  WHEN NOT EXISTS (SELECT 1 FROM prior_txns)
       AND (SELECT count FROM recent_txns) > 1
  THEN 'ALERT: New recurring charge pattern detected'
  ELSE 'NO_ALERT'
END;

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
def parse_alert_to_sql_with_context(transaction: dict, alert_text: str, alert_rule: dict) -> str:
    """
    Inputs: { "transaction": {dict}, "alert_text": str, "alert_rule": dict }
    Returns: SQL query
    """
    client = get_llm_client()
    prompt = build_prompt(transaction, alert_text, alert_rule)
    response = client.invoke(prompt)

    return extract_sql(str(response))
