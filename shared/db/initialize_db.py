import os
import sqlite3
from datetime import datetime

def initialize_db():
    db_path = os.path.join(os.path.dirname(__file__), 'sqlite.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Таблица пользователей (без user_name и language)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        status INTEGER, 
        number_of_events INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP 
        )
    ''')

    # Таблица заказов (добавлены user_name, session_number и language)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS orders (
        order_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        session_number INTEGER,  -- Добавлено поле для хранения номера сессии
        user_name TEXT,  -- Добавлено поле для хранения имени пользователя
        language TEXT,  -- Добавлено поле для хранения языка
        selected_date TIMESTAMP,
        start_time TEXT,
        end_time   TEXT,
        duration   INTEGER,
        people_count INTEGER,
        selected_style TEXT,
        preferences TEXT,
        city TEXT,
        status INTEGER,
        calculated_cost INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(user_id)
        )
    ''')

    # # Вставка тестовых данных - пример для проверки заполнения без начальных данных
    # cursor.execute('''
    #   INSERT INTO users (username, status, number_of_events)
    #   VALUES ('test_user', 1, 2)
    #   ''')
    #
    # cursor.execute('''
    #   INSERT INTO orders (user_id, session_number, user_name, language, selected_date, start_time, end_time, duration, people_count, selected_style, preferences, city, status, calculated_cost)
    #   VALUES (1, 1, 'test_user', 'en', ?, '10:00', '12:00', 2, 5, 'Casual', 'No preferences', 'Test City', 1, 100)
    #   ''', (datetime.now(),))
    #



    conn.commit()
    conn.close()

if __name__ == '__main__':
    initialize_db()
