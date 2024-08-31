# bot/picnic_bot/helpers/db_helpers.py

import sqlite3  # ��� ������ � SQLite
import logging  # ��� �����������
from shared.helpers import create_connection  # ������� ��� �������� ���������� � ����� ������
from shared.config import DATABASE_PATH

def picnic_db_operations(user_id, session_number, update_data=None):
    """
    �������� ������� ��� ���������� �������� � ����� ������ � PicnicBot.

    :param user_id: ������������� ������������ Telegram.
    :param session_number: ����� ������� ������ ������������.
    :param update_data: ������� � ������� ��� ���������� (���� ���������).
    """
    conn = create_connection(DATABASE_PATH)

    if conn is not None:
        try:
            cursor = conn.cursor()

            # �������� ������������� ������
            check_query = "SELECT 1 FROM orders WHERE user_id = ? AND session_number = ?"
            cursor.execute(check_query, (user_id, session_number))
            exists = cursor.fetchone()

            if exists:
                logging.info(f"������ ��� user_id {user_id} � session_number {session_number} ��� ����������.")

                # ���������� ������, ���� update_data �� ������
                if update_data:
                    update_query = "UPDATE orders SET {} WHERE user_id = ? AND session_number = ?".format(
                        ", ".join([f"{key} = ?" for key in update_data.keys()])
                    )
                    cursor.execute(update_query, (*update_data.values(), user_id, session_number))
                    logging.info(f"������ ��� user_id {user_id} � session_number {session_number} ���������.")

            else:
                # �������� ����� ������
                insert_query = """
                    INSERT INTO orders (user_id, session_number, user_name, selected_date, start_time, end_time, 
                                        duration, people_count, selected_style, city, preferences, calculated_cost, status)
                    VALUES (?, ?, null, null, null, null, null, null, null, null, null, null, 1)
                """
                cursor.execute(insert_query, (user_id, session_number))
                logging.info(f"������� ����� ������ ��� user_id {user_id} � session_number {session_number}.")

            conn.commit()

        except sqlite3.Error as e:
            logging.error(f"������ ��� ������ � ����� ������: {e}")
        finally:
            conn.close()
            logging.info("���������� � ����� ������ �������")
    else:
        logging.error("�� ������� ������� ���������� � ����� ������")
