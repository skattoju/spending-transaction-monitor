# agents/sql_executor.py
import os
import sqlite3

import psycopg2
from langchain.tools import tool

# Lazy connection - only connect when needed
conn = None


def get_connection():
    global conn
    if conn is None:
        connection_string = os.getenv('DATABASE_URL')
        if connection_string:
            conn = psycopg2.connect(connection_string)
        else:
            # Fallback to SQLite for testing
            conn = sqlite3.connect('transactions.db')
    return conn


@tool
def execute_sql(sql: str) -> str:
    """Executes a SQL query and returns results or error message."""
    if not sql or sql.strip() == '':
        return 'SQL Error: Empty query'

    cursor = None
    connection = None
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(sql)
        # Otherwise fetch results
        rows = cursor.fetchall()
        return str(rows)

    except Exception as e:
        if connection:
            connection.rollback()
        return f'SQL Error: {e}'

    finally:
        if cursor:
            cursor.close()
