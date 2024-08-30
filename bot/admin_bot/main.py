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


# ORDER_STATUS_REVERSE = {v: k for k, v in ORDER_STATUS.items()}
#
# # Логирование
# logging.basicConfig(
#     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
#     level=logging.INFO,
#     filename=r'C:\Users\USER\PycharmProjects\EventMaster\shared\logs\admin_bot.log'
#     )
# logger = logging.getLogger(__name__)



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
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data.startswith('lang_'):
        # Обработка выбора языка
        language_code = query.data.split('_')[1]
        context.user_data['language'] = language_code

        # После выбора языка показываем основные опции
        await query.message.reply_text(
            "Choose your option:",
            reply_markup=user_options_keyboard(language_code, update.effective_user.id)
        )

# Основной блок запуска бота
if __name__ == '__main__':

    application = ApplicationBuilder().token(BOT_TOKEN).build()
    # Добавляем обработчик команды /start
    application.add_handler(CommandHandler('start', start))

    # Добавляем обработчик нажатий на кнопки (включая выбор языка)
    application.add_handler(CallbackQueryHandler(button_callback))

    application.add_error_handler(lambda update, context: logger.error(f"Update {update} caused error {context.error}"))

    application.run_polling()
