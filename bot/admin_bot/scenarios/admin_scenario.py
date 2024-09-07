# bot/admin_bot/scenarios/admin_scenario.py

import subprocess

import telegram

from bot.admin_bot.helpers.calendar_helpers import generate_calendar_keyboard
from telegram import Update
from telegram.ext import ContextTypes
from bot.admin_bot.keyboards.admin_keyboards import irina_service_menu



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