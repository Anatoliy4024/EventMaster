import sqlite3
import time
from shared.database_logger import log_message, log_query

from shared.config import DATABASE_PATH

def create_connection(db_file):
    """������� ���������� � ����� ������ SQLite, ��������� � db_file."""
    try:
        conn = sqlite3.connect(db_file)
        log_message(f"Database connected: {db_file}")
        return conn
    except sqlite3.Error as e:
        log_message(f"Error connecting to database: {e}")
        return None

def execute_query(conn, query, params=()):
    """��������� SQL-������."""
    if conn is None:
        log_message("No database connection available")
        return False

    try:
        c = conn.cursor()
        log_query(query, params)  # ����������� �������
        c.execute(query, params)
        conn.commit()
        log_message(f"Query executed successfully: {query} with params {params}")
        return True
    except sqlite3.Error as e:
        log_message(f"Error executing query: {e}")
        return False
    finally:
        try:
            conn.close()  # �������� ����������
            log_message("Database connection closed")
        except sqlite3.Error as e:
            log_message(f"Error closing database connection: {e}")

def execute_query_with_retry(conn, query, params=(), max_retries=5):
    """��������� SQL-������ � ���������� ��������� ��� ���������� ���� ������."""
    retries = 0
    while retries < max_retries:
        try:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return True
        except sqlite3.OperationalError as e:
            if "database is locked" in str(e):
                retries += 1
                log_message(f"Database is locked, retrying {retries}/{max_retries}")
                time.sleep(1)  # �������� ����� ��������� ��������
            else:
                log_message(f"Error executing query: {e}")
                return False
        finally:
            if retries >= max_retries:
                log_message(f"Failed to execute query after {max_retries} retries")
                return False
