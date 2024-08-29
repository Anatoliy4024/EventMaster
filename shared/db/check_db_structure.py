import sqlite3
import os

def check_db_structure():
    # Получаем абсолютный путь к файлу базы данных
    db_path = os.path.join(os.path.dirname(__file__), 'sqlite.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Проверяем структуру таблицы orders
    cursor.execute("PRAGMA table_info(orders)")
    columns = cursor.fetchall()

    for column in columns:
        print(column)

    conn.close()

if __name__ == '__main__':
    check_db_structure()
