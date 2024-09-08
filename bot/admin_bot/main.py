## bot/admin_bot/main.py
import nest_asyncio
import asyncio
import os
import sqlite3
import logging
from telegram import Update
from telegram.ext import ContextTypes, ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from shared.config import DATABASE_PATH, BOT_TOKEN, IRA_CHAT_ID, ADMIN_CHAT_ID  # Импортируем ID ДЛЯ СЦЕНАРИЯ ИРИНА И СЕРВИС
from shared.constants import UserData, ORDER_STATUS
from bot.admin_bot.scenarios.user_scenario import send_proforma_to_user, get_full_proforma, get_latest_session_number
from bot.admin_bot.keyboards.admin_keyboards import user_options_keyboard, irina_service_menu, service_menu_keyboard
from bot.admin_bot.scenarios.user_scenario import user_welcome_message
from bot.admin_bot.scenarios.admin_scenario import admin_welcome_message, handle_delete_client_callback, \
    show_calendar_to_admin, handle_date_selection, generate_proforma_buttons_by_date
from bot.admin_bot.scenarios.service_scenario import service_welcome_message

ORDER_STATUS_REVERSE = {v: k for k, v in ORDER_STATUS.items()}


# Определяем путь к файлу лога
log_dir = r'C:\Users\USER\PycharmProjects\EventMaster\bot\admin_bot\helpers\logs'
log_file = os.path.join(log_dir, 'admin_bot.log')

# Создаем директорию, если она не существует
os.makedirs(log_dir, exist_ok=True)

# Настраиваем логирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    filename=log_file,
    encoding='utf-8'
)
logger = logging.getLogger(__name__)

# Подключаем nest_asyncio для обхода ошибки с событийным циклом
nest_asyncio.apply()


# Функция для получения user_id и username по user_id
def get_user_info_by_user_id(user_id):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, username FROM users WHERE user_id = ?", (user_id,))
    user_info = cursor.fetchone()
    conn.close()
    return user_info

# Обработчик команды /start
# Обработчик команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    user_id = user.id  # Получаем user_id пользователя
    user_data = context.user_data.get('user_data', UserData())
    context.user_data['user_data'] = user_data

    # Инициализация переменной message по умолчанию
    message = None
    options_message = None  # Инициализация переменной для опций

    # Проверка ID пользователя
    if user_id == IRA_CHAT_ID:
        # Вызов функции из admin_scenario.py, которая возвращает message и options_message
        message, options_message = await admin_welcome_message(update)

    elif user_id == ADMIN_CHAT_ID:
        # Вызов функции из service_scenario.py, которая возвращает message и options_message
        message, options_message = await service_welcome_message(update)

    else:
        # Обычное приветственное сообщение для других пользователей
        message = await user_welcome_message(update, user.first_name)

    # Сохраняем ID сообщения с кнопками, чтобы потом их заменить
    # Проверяем, была ли переменная `message` и сохраняем её ID, если она существует
    if message:
        context.user_data['language_message_id'] = message.message_id

    # Проверка и сохранение ID сообщения с опциями, если оно существует
    if options_message:
        context.user_data['options_message_id'] = options_message.message_id


# Обработчик нажатий на кнопки
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == 'inactive_button':
        # Эта кнопка неактивна, ничего не делаем
        return

    user_data = context.user_data.get('user_data', UserData())
    context.user_data['user_data'] = user_data

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

    elif query.data == 'delete_client':
        # Нажата кнопка "Удалить клиента"
        await handle_delete_client_callback(update, context)

    if query.data == "yes":
        selected_date = context.user_data.get("selected_date")
        if selected_date:
            # Генерация кнопок для проформ по выбранной дате
            user_id = update.effective_user.id
            proforma_keyboard = await generate_proforma_buttons_by_date(selected_date)
            await query.message.reply_text(f"Проформы для даты {selected_date}:", reply_markup=proforma_keyboard)
        else:
            await query.message.reply_text("Ошибка: выбранная дата не найдена.")
    elif query.data == "no":
        # Возвращение в главное меню
        await admin_welcome_message(update)
        # или если это другой пользователь
        # await service_welcome_message(update)



    # Дополнительные обработчики для других кнопок, например, смены языка и проформы:
    elif query.data.startswith('lang_'):
        language_code = query.data.split('_')[1]
        user_data.set_language(language_code)

        # Удаляем предыдущие сообщения с опциями и проформой
        options_message_id = context.user_data.get('options_message_id')
        proforma_message_id = context.user_data.get('proforma_message_id')

        if options_message_id:
            try:
                await context.bot.delete_message(chat_id=query.message.chat_id, message_id=options_message_id)
            except Exception as e:
                logger.error(f"Error deleting options message: {e}")

        if proforma_message_id:
            try:
                await context.bot.delete_message(chat_id=query.message.chat_id, message_id=proforma_message_id)
            except Exception as e:
                logger.error(f"Error deleting proforma message: {e}")

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

    elif query.data == 'get_proforma':
        try:
            # Получаем user_id пользователя
            user_id = update.effective_user.id

            # Получаем последний session_number для пользователя
            session_number = get_latest_session_number(user_id)

            if session_number:
                # Получаем полную информацию о проформе
                proforma_info = get_full_proforma(user_id, session_number)
                if proforma_info:
                    # Отправляем проформу пользователю
                    proforma_message = await send_proforma_to_user(user_id, session_number, user_data)

                    # Сохраняем ID сообщения с проформой
                    context.user_data['proforma_message_id'] = proforma_message.message_id
                else:
                    await query.message.reply_text(f"Не удалось получить данные проформы для session_number: {session_number}")
            else:
                await query.message.reply_text(f"Не удалось найти session_number для user_id: {user_id}")
        except Exception as e:
            logger.error(f"Ошибка при получении информации о пользователе: {str(e)}")
            await query.message.reply_text("Произошла ошибка при попытке получить информацию о пользователе.")



# функция для запуска из главного main EventMaster
async def run_bot1():
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    # Добавляем необходимые обработчики
    application.add_handler(CommandHandler('start', start))

    application.add_handler(CallbackQueryHandler(handle_date_selection, pattern=r'^date_\d{4}-\d{2}-\d{2}$'))
    application.add_handler(CallbackQueryHandler(button_callback))

    # Добавьте другие ваши обработчики здесь

    # Запуск бота
    await application.run_polling()


# Основной блок
if __name__ == '__main__':
    asyncio.run(run_bot1())


    # старое правильное включение двух ботов в удаленную третью базу)
    # application = ApplicationBuilder().token(BOT_TOKEN).build()
    #
    # application.add_handler(CommandHandler('start', start))
    # application.add_handler(CallbackQueryHandler(button_callback))
    #
    # application.run_polling()

