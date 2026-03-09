import os
import pymysql
from pymysql.cursors import DictCursor

DB_CONFIG = {
    'host': os.environ.get('DB_HOST', 'localhost'),
    'user': os.environ.get('DB_USER', 'root'),
    'password': os.environ.get('DB_PASSWORD', 'mysql123'),
    'database': os.environ.get('DB_NAME', 'back2me_db'),
    'cursorclass': DictCursor, # Returns dicts instead of tuples
    'autocommit': True
}

def get_db_connection():
    """Returns a direct MySQL connection."""
    try:
        return pymysql.connect(**DB_CONFIG)
    except Exception as err:
        print(f"Database connection error: {err}")
        return None

def execute_query(query, params=(), fetchone=False, fetchall=False):
    """Utility to execute query and fetch results safely."""
    conn = get_db_connection()
    if not conn:
        return None
        
    try:
        with conn.cursor() as cursor:
            cursor.execute(query, params)
            if fetchone:
                return cursor.fetchone()
            if fetchall:
                return cursor.fetchall()
            return cursor.lastrowid # For inserts
    except Exception as e:
        print(f"Database Query Error: {e}")
        raise e
    finally:
        conn.close()
