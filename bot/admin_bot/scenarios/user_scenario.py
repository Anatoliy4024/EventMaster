import sqlite3
import logging
from telegram import Update
from telegram.ext import ContextTypes
from bot.admin_bot.helpers.database_helpers import send_proforma_to_user, get_latest_session_number, get_full_proforma
from bot.admin_bot.keyboards.admin_keyboards import user_options_keyboard
from shared.constants import UserData, ORDER_STATUS

from shared.config import DATABASE_PATH

ORDER_STATUS_REVERSE = {v: k for k, v in ORDER_STATUS.items()}

import logging

# Логирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    filename=r'C:\Users\USER\PycharmProjects\EventMaster\shared\logs\admin_bot.log'  # Укажите путь к файлу лога
)
logger = logging.getLogger(__name__)

async def handle_proforma_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_data = context.user_data.get('user_data', UserData())
    context.user_data['user_data'] = user_data

    if query.data.startswith('lang_'):
        language_code = query.data.split('_')[1]
        user_data.set_language(language_code)

        # Удаляем предыдущие сообщения с опциями и проформой
        options_message_id = context.user_data.get('options_message_id')
        proforma_message_id = context.user_data.get('proforma_message_id')

        if options_message_id:
            try:
                await context.bot.delete_message(chat_id=query.message.chat_id, message_id=options_message_id)
            except Exception as e:
                logging.error(f"Error deleting options message: {e}")

        if proforma_message_id:
            try:
                await context.bot.delete_message(chat_id=query.message.chat_id, message_id=proforma_message_id)
            except Exception as e:
                logging.error(f"Error deleting proforma message: {e}")

        # Отправляем новые кнопки в соответствии с выбранным языком и заголовок
        headers = {
            'en': "Choose",
            'ru': "Выбери",
            'es': "Elige",
            'fr': "Choisissez",
            'uk': "Виберіть",
            'pl': "Wybierz",
            'de': "Wählen",
            'it': "Scegli"
        }

        user_id = update.effective_user.id  # Получаем user_id пользователя
        new_options_message = await query.message.reply_text(
            headers.get(language_code, "Choose"),
            reply_markup=user_options_keyboard(language_code, user_id)
        )

        # Обновляем ID сообщения с новыми опциями
        context.user_data['options_message_id'] = new_options_message.message_id
    elif query.data == 'get_proforma':  # Было 'get_full_proforma', заменили на 'get_proforma'
        try:
            # Получаем user_id пользователя
            user_id = update.effective_user.id

            # Получаем последний session_number для пользователя
            session_number = get_latest_session_number(user_id)

            if session_number:
                # Отправляем проформу пользователю
                proforma_message = await send_proforma_to_user(user_id, session_number, user_data)

                # Сохраняем ID сообщения с проформой
                context.user_data['proforma_message_id'] = proforma_message.message_id

            else:
                await query.message.reply_text(f"Не удалось найти session_number для user_id: {user_id}")
        except Exception as e:
            logger.error(f"Ошибка при получении информации о пользователе: {str(e)}")
            await query.message.reply_text("Произошла ошибка при попытке получить информацию о пользователе.")
