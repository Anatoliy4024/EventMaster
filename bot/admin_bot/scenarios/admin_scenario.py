## bot/admin_bot/scenarios/admin_scenario.py
import sqlite3
import subprocess

import logging
import telegram

from bot.admin_bot.helpers.calendar_helpers import generate_calendar_keyboard
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from bot.admin_bot.keyboards.admin_keyboards import irina_service_menu, yes_no_keyboard
from shared.config import DATABASE_PATH
from shared.helpers import create_connection
from bot.admin_bot.helpers.calendar_helpers import disable_calendar_buttons






async def admin_welcome_message(update: Update):
    # Приветственное сообщение для Администратора
    message = await update.message.reply_text(
        "Привет, Иринушка! Я - твой АдминБот."
    )
    # Отображаем меню с 3 кнопками для Ирины
    options_message = await update.message.reply_text(
        "Выбери действие:",
        reply_markup=irina_service_menu()
    )
    return message, options_message


# Функция для показа календаря и редактирования сообщения
async def show_calendar_to_admin(update, context, month_offset=0):
    query = update.callback_query

    # Генерация календаря с учетом смещения месяца
    calendar_markup = generate_calendar_keyboard(month_offset)

    try:
        # Редактируем текущее сообщение, а не отправляем новое
        await query.edit_message_reply_markup(reply_markup=calendar_markup)
    except telegram.error.BadRequest as e:
        # Обработка ошибки, если сообщение уже было отредактировано
        if str(e) == "Message is not modified":
            pass
        else:
            raise

    # Обработка нажатий на календарь
    if query.data.startswith('prev_month_'):
        # Извлекаем смещение месяца для предыдущего месяца
        month_offset = int(query.data.split('_')[2])  # Извлекаем корректную часть callback_data
        await show_calendar_to_admin(update, context, month_offset)

    elif query.data.startswith('next_month_'):
         # Извлекаем смещение месяца для следующего месяца
         month_offset = int(query.data.split('_')[2])  # Извлекаем корректную часть callback_data
         await show_calendar_to_admin(update, context, month_offset)

    elif query.data == 'show_calendar':
         # Нажата кнопка "Показать календарь"
        await show_calendar_to_admin(update, context)



async def handle_delete_client_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обрабатывает нажатие на кнопку 'Удалить клиента из базы данных'.
    """
    await show_calendar_to_admin(update, context)



def extract_date_from_callback(callback_data):
    """
    Функция для извлечения даты из callback_data кнопки с красным флажком или без.
    Ожидаемые форматы:
    - 'date_YYYY-MM-DD'
    - 'reserved_date_YYYY-MM-DD'
    """
    if callback_data.startswith('date_'):
        return callback_data.split('_')[1]
    elif callback_data.startswith('reserved_date_'):
        return callback_data.split('_')[2]
    else:
        return None


async def handle_date_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data

    if data.startswith('reserved_date_'):
        # Дата с красным флажком, например, reserved_date_2024-09-12
        selected_date = data.split('_')[2]

        # Логика обработки выбранной даты
        confirmation_message = f"Вы выбрали дату {selected_date}, правильно?"

        # Создаем кнопки "Да" и "Нет"
        buttons = [
            [InlineKeyboardButton("Да", callback_data="yes"),
             InlineKeyboardButton("Нет", callback_data="no")]
        ]
        keyboard = InlineKeyboardMarkup(buttons)

        # Отправляем сообщение с подтверждением и кнопками
        await query.message.reply_text(confirmation_message, reply_markup=keyboard)



async def handle_calendar_navigation(update, context):
    query = update.callback_query
    data = query.data

    if data.startswith('date_'):
        # Получаем дату с помощью функции
        selected_date = extract_date_from_callback(data)

        if selected_date:
            # Отключаем все остальные кнопки и оставляем выбранную с красной точкой
            #from bot.admin_bot.scenarios.admin_scenario import disable_calendar_buttons
            new_reply_markup = disable_calendar_buttons(query.message.reply_markup, selected_date)
            await query.edit_message_reply_markup(reply_markup=new_reply_markup)

            # Переход на следующий шаг — формирование кнопок для проформ
            await query.message.reply_text(f"Вы выбрали дату {selected_date}. Формирую проформы...")

async def generate_proforma_buttons_by_date(user_id, selected_date):
    conn = create_connection(DATABASE_PATH)
    buttons = []
    if conn is not None:
        try:
            # Извлекаем все заказы для user_id, у которых дата совпадает с выбранной датой
            select_query = "SELECT session_number, status FROM orders WHERE user_id = ? AND selected_date = ?"
            cursor = conn.cursor()
            cursor.execute(select_query, (user_id, selected_date))
            orders = cursor.fetchall()

            # Генерируем кнопки для каждой проформы с номером
            for order in orders:
                session_number, status = order
                proforma_number = f"{user_id}_{session_number}_{status}"

                # Добавляем кнопку с номером проформы
                buttons.append(
                    [InlineKeyboardButton(f"Проформа {proforma_number}", callback_data=f"proforma_{proforma_number}")]
                )

        except sqlite3.Error as e:
            logging.error(f"Ошибка при работе с базой данных: {e}")
        finally:
            conn.close()

    # Возвращаем InlineKeyboardMarkup с кнопками проформ
    return InlineKeyboardMarkup(buttons)
