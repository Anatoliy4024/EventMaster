import logging
import sqlite3

# Настройка логирования
logging.basicConfig(
    filename='db_operations.log',
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    encoding='utf-8'  # Добавьте эту строку для установки кодировки UTF-8
)

def log_message(message):
    logging.info(message)

def log_query(query, params=()):
    logging.info(f'Executing query: {query} with params: {params}')

def execute_query_with_logging(conn, query, params=()):
    try:
        cursor = conn.cursor()
        log_query(query, params)
        cursor.execute(query, params)
        conn.commit()
        log_message('Query executed successfully.')
    except sqlite3.Error as e:
        log_message(f'Error executing query: {e}')
