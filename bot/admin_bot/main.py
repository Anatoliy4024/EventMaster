import sqlite3

from shared.translations import language_selection_keyboard  # Импортируем клавиатуру выбора языка
from keyboards.admin_keyboards import user_options_keyboard

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from shared.config import DATABASE_PATH, BOT_TOKEN, IRA_CHAT_ID, ADMIN_CHAT_ID
from shared.constants import ORDER_STATUS

# Настройка логгирования с использованием UTF-8
file_handler = logging.FileHandler(
    filename=r'C:\Users\USER\PycharmProjects\EventMaster\shared\logs\admin_bot.log',
    encoding='utf-8'
)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(file_handler)

# Пример записи в лог
logger.info("Логирование настроено с поддержкой UTF-8.")

# Далее идет ваша основная логика
ORDER_STATUS_REVERSE = {v: k for k, v in ORDER_STATUS.items()}


# Обработчик для команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    user_id = user.id

    # Приветствие и выбор языка
    message = await update.message.reply_text(
        f"Welcome {user.first_name}! Choose your language / Выберите язык",
        reply_markup=language_selection_keyboard()
    )

    # Сохраняем ID сообщения с выбором языка
    context.user_data['language_message_id'] = message.message_id

# Обработчик нажатий на кнопки (включая выбор языка)
# Обработчик нажатий на кнопки (включая выбор языка)
# Обработчик нажатий на кнопки (включая выбор языка)
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data.startswith('lang_'):
        # Обработка выбора языка
        language_code = query.data.split('_')[1]
        context.user_data['language'] = language_code

        # Удаляем предыдущие сообщения с опциями, если они есть
        options_message_id = context.user_data.get('options_message_id')
        if options_message_id:
            try:
                await context.bot.delete_message(chat_id=query.message.chat_id, message_id=options_message_id)
            except Exception as e:
                logger.error(f"Error deleting options message: {e}")

        # Заголовок в зависимости от выбранного языка
        headers = {
            'en': "Choose your option:",
            'ru': "Выберите действие:",
            'es': "Elige una opción:",
            'fr': "Choisissez une option:",
            'uk': "Виберіть дію:",
            'pl': "Wybierz opcję:",
            'de': "Wählen Sie eine Option:",
            'it': "Scegli un'opzione:"
        }

        # Отправляем новые кнопки с текстом на выбранном языке
        new_options_message = await query.message.reply_text(
            headers.get(language_code, "Choose your option:"),
            reply_markup=user_options_keyboard(language_code, update.effective_user.id)
        )

        # Сохраняем ID сообщения с новыми опциями
        context.user_data['options_message_id'] = new_options_message.message_id

# Основной блок запуска бота
if __name__ == '__main__':

    application = ApplicationBuilder().token(BOT_TOKEN).build()
    # Добавляем обработчик команды /start
    application.add_handler(CommandHandler('start', start))

    # Добавляем обработчик нажатий на кнопки (включая выбор языка)
    application.add_handler(CallbackQueryHandler(button_callback))

    application.add_error_handler(lambda update, context: logger.error(f"Update {update} caused error {context.error}"))

    application.run_polling()
