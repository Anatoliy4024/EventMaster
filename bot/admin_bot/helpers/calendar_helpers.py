from datetime import datetime, timedelta
import calendar
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import sqlite3
from shared.config import DATABASE_PATH  # Путь к базе данных

def get_dates_with_active_proformas():
    """
    Получает даты, на которые есть хотя бы одна проформа со статусом >= 3.
    """
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT DISTINCT selected_date 
            FROM orders 
            WHERE status >= 3
        """)
        dates = cursor.fetchall()  # Получаем все даты, на которые есть активные проформы
        return [date[0] for date in dates]  # Возвращаем список дат в формате YYYY-MM-DD
    finally:
        conn.close()

def check_date_reserved(date, reserved_dates):
    """Проверяет, зарезервирована ли дата."""
    return date in reserved_dates

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from datetime import datetime, timedelta
import calendar

# bot/admin_bot/helpers/calendar_helpers.py
from datetime import datetime, timedelta
import calendar
import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def to_superscript(num_str):
    superscript_map = str.maketrans('0123456789', '⁰¹²³⁴⁵⁶⁷⁸⁹')
    return num_str.translate(superscript_map)

def generate_month_name(month, language):
    months = {
        'en': ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
        'ru': ["Янв", "Фев", "Мар", "Апр", "Май", "Июн", "Июл", "Авг", "Сен", "Окт", "Ноя", "Дек"],
        # Добавьте другие языки по необходимости
    }
    return months[language][month - 1]

def generate_calendar_keyboard(month_offset=0, language='en'):
    today = datetime.today()
    base_month = today.month + month_offset
    base_year = today.year

    if base_month > 12:
        base_month -= 12
        base_year += 1
    elif base_month < 1:
        base_month += 12
        base_year -= 1

    first_of_month = datetime(base_year, base_month, 1)
    last_day = calendar.monthrange(first_of_month.year, first_of_month.month)[1]
    last_of_month = first_of_month.replace(day=last_day)

    month_name = generate_month_name(first_of_month.month, language)

    days_of_week = {
        'en': ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
        'ru': ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"],
    }

    calendar_buttons = [[InlineKeyboardButton(day, callback_data='none')] for day in days_of_week[language]]
    start_weekday = first_of_month.weekday()
    current_date = first_of_month

    # Заполняем календарь днями месяца
    for _ in range(5):  # 5 строк (максимум) для дней месяца
        for day in range(len(calendar_buttons)):
            if current_date.day == 1 and day < start_weekday:
                calendar_buttons[day].append(InlineKeyboardButton(" ", callback_data='none'))
            elif current_date > last_of_month:
                calendar_buttons[day].append(InlineKeyboardButton(" ", callback_data='none'))
            else:
                day_text = to_superscript(str(current_date.day))
                calendar_buttons[day].append(InlineKeyboardButton(f" {current_date.day}", callback_data=f'date_{current_date.strftime("%Y-%m-%d")}'))
                current_date += timedelta(days=1)

    prev_month_button = InlineKeyboardButton("<", callback_data=f"prev_month_{month_offset - 1}")
    next_month_button = InlineKeyboardButton(">", callback_data=f"next_month_{month_offset + 1}")
    month_name_button = InlineKeyboardButton(f"{month_name} {first_of_month.year}", callback_data="none")

    calendar_buttons.append([prev_month_button, month_name_button, next_month_button])

    return InlineKeyboardMarkup(calendar_buttons)

def disable_calendar_buttons(reply_markup, selected_date):
    new_keyboard = []
    for row in reply_markup.inline_keyboard:
        new_row = []
        for button in row:
            if button.callback_data and button.callback_data.endswith(selected_date):
                new_row.append(InlineKeyboardButton(f"🔴 {selected_date.split('-')[2]}", callback_data='none'))
            else:
                new_row.append(InlineKeyboardButton(button.text, callback_data='none'))
        new_keyboard.append(new_row)
    return InlineKeyboardMarkup(new_keyboard)
