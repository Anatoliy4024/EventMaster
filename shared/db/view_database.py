import os
import sqlite3

def fetch_all_users():
    # Определяем путь к базе данных относительно текущего файла
    db_path = os.path.join(os.path.dirname(__file__), 'sqlite.db')

    if not os.path.exists(db_path):
        print(f"База данных не найдена по пути: {db_path}")
        return

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        # Закомментируйте строки, которые вам не нужны или расскомментируйте необходимые
        # cursor.execute("SELECT * FROM user_sessions")
        cursor.execute("SELECT * FROM orders")
        rows = cursor.fetchall()
        for row in rows:
            print(row)
    except sqlite3.Error as e:
        print(f"Ошибка при работе с базой данных: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    fetch_all_users()
