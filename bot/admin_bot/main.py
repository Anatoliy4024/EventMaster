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
    show_calendar_to_admin, handle_date_selection, generate_proforma_buttons_by_date, handle_proforma_button_click, \
    handle_find_client_callback, null_status
from bot.admin_bot.scenarios.service_scenario import service_welcome_message
from shared.translations import language_selection_keyboard

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

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    user_id = user.id  # Получаем user_id пользователя
    user_data = context.user_data.get('user_data', UserData())
    context.user_data["delete_messages"] = list()
    context.user_data['user_data'] = user_data

    # Инициализация переменной message по умолчанию
    message = None

    # Проверка ID пользователя
    if user_id == IRA_CHAT_ID:
        # Вызываем функцию для выбора языка и меню администратора
        message = await admin_welcome_message(update)
    elif user_id == ADMIN_CHAT_ID:
        # Вызов функции для другого администратора
        message, _ = await service_welcome_message(update)
    else:
        # Обычное приветственное сообщение для других пользователей
        message = await user_welcome_message(update, user.first_name)

    # Сохраняем ID сообщения с кнопками
    if message:
        context.user_data['language_message_id'] = message.message_id


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
        month_offset = int(query.data.split('_')[2])  # Извлекаем смещение месяца
        await show_calendar_to_admin(update, context, month_offset)

    elif query.data.startswith('next_month_'):
        month_offset = int(query.data.split('_')[2])  # Извлекаем смещение месяца
        await show_calendar_to_admin(update, context, month_offset)

    elif query.data == 'show_calendar':
        await show_calendar_to_admin(update, context)

    elif query.data == 'find_and_view_order':
        user_data.set_step('find_and_view_order')
        await handle_find_client_callback(update, context)

    elif query.data == 'delete_client':
        user_data.set_step('delete_client')
        await handle_delete_client_callback(update, context)

    elif query.data == "yes":
        selected_date = context.user_data.get("selected_date")
        if user_data.get_step().startswith("delete_client_"):
            order_id = user_data.get_step().split("_")[-1]
            null_status(order_id)

            # Удаляем предыдущие сообщения с опциями и проформой
            del_message_id = context.user_data.get("delete_messages")
            if del_message_id:

                for i in del_message_id:
                    try:
                        await context.bot.delete_message(chat_id=query.message.chat_id, message_id=i)
                    except Exception as e:
                        logger.error(f"Error deleting options message: {e}")

            # Если это администратор, переключаем на админ-меню
            if update.effective_user.id == IRA_CHAT_ID:
                options_message = await query.message.reply_text(
                    "Выбери действие:",
                    reply_markup=irina_service_menu()
                )
                # context.user_data['options_message_id'] = options_message.message_id
                context.user_data['delete_messages'].append(options_message.message_id)
            else:
                # Для других пользователей остается логика стандартного меню юзера
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

                new_options_message = await query.message.reply_text(
                    headers.get(user_data.get_language(), "Choose"),
                    reply_markup=user_options_keyboard(user_data.get_language(), update.effective_user.id)
                )

                # context.user_data['options_message_id'] = new_options_message.message_id
                context.user_data['delete_messages'].append(new_options_message.message_id)


        elif selected_date:
            # Генерация кнопок для проформ по выбранной дате
            admin_id = IRA_CHAT_ID  # Указываем ID администратора
            proforma_keyboard = await generate_proforma_buttons_by_date(selected_date)
            message = await context.bot.send_message(
                chat_id=admin_id,
                text=f"Проформы для даты {selected_date}:",
                reply_markup=proforma_keyboard
            )
            context.user_data['delete_messages'].append(message.message_id)

        else:
            message = await query.message.reply_text("Ошибка: выбранная дата не найдена.")
            context.user_data['delete_messages'].append(message.message_id)
    elif query.data == "no":
        # Удаляем предыдущие сообщения с календарем и подтверждением даты
        del_message_id = context.user_data.get("delete_messages")
        if del_message_id:
            for i in del_message_id:
                try:
                    await context.bot.delete_message(chat_id=query.message.chat_id, message_id=i)
                except Exception as e:
                    logger.error(f"Error deleting message: {e}")

        # Если это администратор, переключаем на админ-меню
        if update.effective_user.id == IRA_CHAT_ID:
            options_message = await query.message.reply_text(
                "Выбери действие:",
                reply_markup=irina_service_menu()
            )
            context.user_data['delete_messages'] = [options_message.message_id]  # Сохраняем ID сообщения

        else:
            # Логика для других пользователей
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

            new_options_message = await query.message.reply_text(
                headers.get(user_data.get_language(), "Choose"),
                reply_markup=user_options_keyboard(user_data.get_language(), update.effective_user.id)
            )
            context.user_data['delete_messages'] = [new_options_message.message_id]

        # Возвращение в главное меню администратора
        await admin_welcome_message(update)

    # Обработка нажатий на кнопки смены языка
    elif query.data.startswith('lang_'):
        language_code = query.data.split('_')[1]
        user_data.set_language(language_code)

        # Удаляем предыдущие сообщения с опциями и проформой
        del_message_id = context.user_data.get("delete_messages")
        if del_message_id:

            for i in del_message_id:
                try:
                    await context.bot.delete_message(chat_id=query.message.chat_id, message_id=i)
                except Exception as e:
                    logger.error(f"Error deleting options message: {e}")

        # Если это администратор, переключаем на админ-меню
        if update.effective_user.id == IRA_CHAT_ID:
            options_message = await query.message.reply_text(
                "Выбери действие:",
                reply_markup=irina_service_menu()
            )
            # context.user_data['options_message_id'] = options_message.message_id
            context.user_data['delete_messages'].append(options_message.message_id)
        else:
            # Для других пользователей остается логика стандартного меню юзера
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

            new_options_message = await query.message.reply_text(
                headers.get(language_code, "Choose"),
                reply_markup=user_options_keyboard(language_code, update.effective_user.id)
            )

            # context.user_data['options_message_id'] = new_options_message.message_id
            context.user_data['delete_messages'].append(new_options_message.message_id)

    # Обработка кнопки для получения проформы
    elif query.data == 'get_proforma':
        try:
            admin_id = IRA_CHAT_ID  # Указываем ID администратора
            session_number = get_latest_session_number(admin_id)

            if session_number:
                proforma_info = get_full_proforma(admin_id, session_number)
                if proforma_info:
                    proforma_message = await send_proforma_to_user(admin_id, session_number, user_data)

                    # context.user_data['proforma_message_id'] = proforma_message.message_id
                    context.user_data['delete_messages'].append(proforma_message.message_id)

                else:
                    await query.message.reply_text(f"Не удалось получить данные проформы для session_number: {session_number}")
            else:
                await query.message.reply_text(f"Не удалось найти session_number для admin_id: {admin_id}")
        except Exception as e:
            logger.error(f"Ошибка при получении информации о проформе: {str(e)}")
            await query.message.reply_text("Произошла ошибка при попытке получить информацию о проформе.")


# функция для запуска из главного main EventMaster
async def run_bot1():
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    # Добавляем необходимые обработчики
    application.add_handler(CommandHandler('start', start))

    # Обработчик для выбора даты
    application.add_handler(CallbackQueryHandler(handle_date_selection, pattern=r'^date_\d{4}-\d{2}-\d{2}$'))

    # Обработчик для кнопок проформы
    application.add_handler(CallbackQueryHandler(handle_proforma_button_click, pattern=r'^\d+_\d+_\d+$'))  # Обработчик проформ

    # Обработчик для других кнопок
    application.add_handler(CallbackQueryHandler(button_callback))

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
