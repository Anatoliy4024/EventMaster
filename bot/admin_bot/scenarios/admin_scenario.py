# bot/admin_bot/scenarios/admin_scenario.py

import subprocess
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


async def show_calendar_to_admin(update: Update, context: ContextTypes.DEFAULT_TYPE, month_offset=0):
    query = update.callback_query
    await query.answer()

    # Генерация календаря с текущим или выбранным месяцем
    calendar_markup = generate_calendar_keyboard(month_offset=month_offset)

    # Отправляем сообщение с календарем
    await query.message.reply_text(
        text="Выберите дату для просмотра активных проформ:",
        reply_markup=calendar_markup
    )


async def handle_delete_client_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Здесь можно добавить код для обработки удаления клиента
    await show_calendar_to_admin(update, context)  # Временно показываем календарь при удалении


async def handle_delete_client_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обрабатывает нажатие на кнопку 'Удалить клиента из базы данных'.
    """
    await show_calendar_to_admin(update, context)
