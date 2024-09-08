## bot/admin_bot/scenarios/admin_scenario.py
import sqlite3
import subprocess

import logging
from asyncio.log import logger

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
        logger.info(f"Попытка редактировать сообщение с новым календарем для месяца offset: {month_offset}")
        await query.edit_message_reply_markup(reply_markup=calendar_markup)
    except telegram.error.BadRequest as e:
        # Обработка ошибки, если сообщение уже было отредактировано
        if str(e) == "Message is not modified":
            logger.warning(f"Сообщение не изменилось. Ошибка: {str(e)}")
            pass
        else:
            logger.error(f"Произошла ошибка при редактировании сообщения: {str(e)}")
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

    if data.startswith('date_'):
        # Извлекаем выбранную дату
        selected_date = data.split('_')[1]
        logging.info(f"Selected date: {selected_date}")  # Логируем дату

        # Сохраняем выбранную дату в контексте
        context.user_data['selected_date'] = selected_date
        logging.info(f"Context date saved: {context.user_data['selected_date']}")  # Логируем сохраненную дату

        # Отключаем остальные кнопки и оставляем выбранную с красной точкой
        new_reply_markup = disable_calendar_buttons(query.message.reply_markup, selected_date)
        await query.edit_message_reply_markup(reply_markup=new_reply_markup)

        # Подтверждаем выбор даты
        await query.message.reply_text(f"Вы выбрали дату {selected_date}, правильно?", reply_markup=yes_no_keyboard('ru'))

    elif query.data == "yes":
        selected_date = context.user_data.get("selected_date")
        logging.info(f"User confirmed date: {selected_date}")  # Логируем подтвержденную дату

        if selected_date:
            # Получаем user_id
            user_id = update.effective_user.id
            logging.info(f"User ID: {user_id}, Selected Date: {selected_date}")  # Логируем user_id и дату

            # Генерируем кнопки для проформ по выбранной дате
            selected_date = context.user_data.get("selected_date")
            proforma_keyboard = await generate_proforma_buttons_by_date(selected_date)
            await query.message.reply_text(f"Проформы для даты {selected_date}:", reply_markup=proforma_keyboard)
        else:
            await query.message.reply_text("Ошибка: выбранная дата не найдена.")


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


def generate_proforma_buttons(proforma_list):
    keyboard = []
    for proforma in proforma_list:
        # Формируем полный номер проформы: user_id, session_number, status
        full_proforma_number = f"{proforma['user_id']}_{proforma['session_number']}_{proforma['status']}"
        keyboard.append(
            [InlineKeyboardButton(full_proforma_number, callback_data=f"proforma_{proforma['session_number']}")])

    return InlineKeyboardMarkup(keyboard)

