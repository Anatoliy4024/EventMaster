# bot/picnic_bot/helpers/db_helpers.py

import sqlite3  # для работы с SQLite
import logging  # для логирования
from shared.helpers import create_connection  # функция для создания соединения с базой данных
from shared.config import DATABASE_PATH

def picnic_db_operations(user_id, session_number, update_data=None):
    """
    Основная функция для выполнения операций с базой данных в PicnicBot.

    :param user_id: Идентификатор пользователя Telegram.
    :param session_number: Номер текущей сессии пользователя.
    :param update_data: Словарь с данными для обновления (если требуется).
    """
    conn = create_connection(DATABASE_PATH)

    if conn is not None:
        try:
            cursor = conn.cursor()

            # Проверка существования записи
            check_query = "SELECT 1 FROM orders WHERE user_id = ? AND session_number = ?"
            cursor.execute(check_query, (user_id, session_number))
            exists = cursor.fetchone()

            if exists:
                logging.info(f"Запись для user_id {user_id} и session_number {session_number} уже существует.")

                # Обновление записи, если update_data не пустой
                if update_data:
                    update_query = "UPDATE orders SET {} WHERE user_id = ? AND session_number = ?".format(
                        ", ".join([f"{key} = ?" for key in update_data.keys()])
                    )
                    cursor.execute(update_query, (*update_data.values(), user_id, session_number))
                    logging.info(f"Запись для user_id {user_id} и session_number {session_number} обновлена.")

            else:
                # Создание новой записи
                insert_query = """
                    INSERT INTO orders (user_id, session_number, user_name, selected_date, start_time, end_time, 
                                        duration, people_count, selected_style, city, preferences, calculated_cost, status)
                    VALUES (?, ?, null, null, null, null, null, null, null, null, null, null, 1)
                """
                cursor.execute(insert_query, (user_id, session_number))
                logging.info(f"Создана новая запись для user_id {user_id} и session_number {session_number}.")

            conn.commit()

        except sqlite3.Error as e:
            logging.error(f"Ошибка при работе с базой данных: {e}")
        finally:
            conn.close()
            logging.info("Соединение с базой данных закрыто")
    else:
        logging.error("Не удалось создать соединение с базой данных")
