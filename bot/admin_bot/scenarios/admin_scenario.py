## bot/admin_bot/scenarios/admin_scenario.py
import sqlite3
import subprocess

import logging
from asyncio.log import logger
import telegram
from bot.admin_bot.helpers.calendar_helpers import generate_calendar_keyboard
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from bot.admin_bot.helpers.database_helpers import get_full_proforma
from bot.admin_bot.keyboards.admin_keyboards import irina_service_menu, yes_no_keyboard
from shared.config import DATABASE_PATH
from shared.constants import UserData
from shared.helpers import create_connection
from bot.admin_bot.helpers.calendar_helpers import disable_calendar_buttons
from shared.translations import translations, language_selection_keyboard


async def admin_welcome_message(update: Update):
    # Приветственное сообщение для выбора языка
    message = await update.message.reply_text(
        "Привет, администратор! Я - твой АдминБот. Выбери язык / Choose your language:",
        reply_markup=language_selection_keyboard()
    )
    return message




# async def admin_welcome_message(update: Update):
#     # Приветственное сообщение для Администратора
#     message = await update.message.reply_text(
#         "Привет, Иринушка! Я - твой АдминБот."
#     )
#     # Отображаем меню с 3 кнопками для Ирины
#     options_message = await update.message.reply_text(
#         "Выбери действие:",
#         reply_markup=irina_service_menu()
#     )
#     return message, options_message


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
async def handle_find_client_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обрабатывает нажатие на кнопку 'Удалить клиента из базы данных'.
    """
    await show_calendar_to_admin(update, context)


# def extract_date_from_callback(callback_data):
#     """
#     Функция для извлечения даты из callback_data кнопки с красным флажком или без.
#     Ожидаемые форматы:
#     - 'date_YYYY-MM-DD'
#     - 'reserved_date_YYYY-MM-DD'
#     """
#     if callback_data.startswith('date_'):
#         return callback_data.split('_')[1]
#     elif callback_data.startswith('reserved_date_'):
#         return callback_data.split('_')[2]
#     else:
#         return None
#


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
        message = await query.message.reply_text(f"Вы выбрали дату {selected_date}, правильно?", reply_markup=yes_no_keyboard('ru'))

        context.user_data['delete_messages'].append(message.message_id)

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
            message = await query.message.reply_text(f"Проформы для даты {selected_date}:", reply_markup=proforma_keyboard)
            context.user_data['delete_messages'].append(message.message_id)

        else:
            await query.message.reply_text("Ошибка: выбранная дата не найдена.")


# async def handle_calendar_navigation(update, context):
#     query = update.callback_query
#     data = query.data
#
#     if data.startswith('date_'):
#         # Получаем дату с помощью функции
#         selected_date = extract_date_from_callback(data)
#
#         if selected_date:
#             # Отключаем все остальные кнопки и оставляем выбранную с красной точкой
#             #from bot.admin_bot.scenarios.admin_scenario import disable_calendar_buttons
#             new_reply_markup = disable_calendar_buttons(query.message.reply_markup, selected_date)
#             await query.edit_message_reply_markup(reply_markup=new_reply_markup)
#
#             # Переход на следующий шаг — формирование кнопок для проформ
#             await query.message.reply_text(f"Вы выбрали дату {selected_date}. Формирую проформы...")


def generate_proforma_buttons(proforma_list):
    keyboard = []
    for proforma in proforma_list:
        # Формируем полный номер проформы: user_id, session_number, status
        full_proforma_number = f"{proforma['user_id']}_{proforma['session_number']}_{proforma['status']}"
        keyboard.append(
            [InlineKeyboardButton(full_proforma_number, callback_data=f"proforma_{proforma['session_number']}")])

    return InlineKeyboardMarkup(keyboard)


async def generate_proforma_buttons_by_date(selected_date):
    # Пример запроса в базу данных
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    try:
        # Предполагается, что вам нужно получить проформы по дате
        cursor.execute("""
            SELECT user_id, session_number, status
            FROM orders
            WHERE selected_date = ? AND status >= 3
        """, (selected_date,))

        proforma_list = cursor.fetchall()

        if not proforma_list:
            return None  # Если проформы не найдены

        # Генерация кнопок для проформ
        buttons = []
        for proforma in proforma_list:
            proforma_number = f"{proforma[0]}_{proforma[1]}_{proforma[2]}"

            # Выводим callback_data в консоль для проверки
            print(f"Callback data для кнопки: {proforma_number}")

            # callback_data = f"{proforma['user_id']}_{proforma['session_number']}_{proforma['status']}"
            # buttons.append([InlineKeyboardButton(proforma_number, callback_data=callback_data)])

            buttons.append([InlineKeyboardButton(proforma_number, callback_data=f"{proforma[0]}_{proforma[1]}_{proforma[2]}")])

        return InlineKeyboardMarkup(buttons)

    finally:
        conn.close()


async def handle_proforma_button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data = context.user_data.get('user_data', UserData())

    query = update.callback_query
    proforma_data = query.data.split('_')

    # Проверяем, что данные проформы корректны
    if len(proforma_data) == 3:
        user_id = proforma_data[0]
        session_number = proforma_data[1]
        status = proforma_data[2]

        # Логируем для отладки
        print(f"user_id: {user_id}, session_number: {session_number}, status: {status}")

        # Попробуем получить информацию о проформе
        try:
            proforma_info = get_full_proforma(user_id, session_number)
            if proforma_info:
                # Формируем текст сообщения для отправки админу
                full_proforma_text = (
                    f"Полная информация по проформе:\n\n"
                    f"User ID: {proforma_info[0]}\n"
                    f"Session Number: {proforma_info[1]}\n"
                    f"Дата события: {proforma_info[2]}\n"
                    f"Время: {proforma_info[3]} - {proforma_info[4]}\n"
                    f"Количество участников: {proforma_info[5]}\n"
                    f"Стиль мероприятия: {proforma_info[6]}\n"
                    f"Город: {proforma_info[7]}\n"
                    f"Стоимость: {proforma_info[8]} евро\n"
                    f"Статус: {proforma_info[10]}"
                )
                message = await query.message.reply_text(full_proforma_text)
                context.user_data['delete_messages'].append(message.message_id)

                if user_data.get_step() == "delete_client":
                    user_data.set_step(f"delete_client_{proforma_info[11]}")
                    message = await query.message.reply_text(f"удалить эту запись?",
                                                   reply_markup=yes_no_keyboard('ru'))
                    context.user_data['delete_messages'].append(message.message_id)


                #     формируем кнопки
            else:
                message = await query.message.reply_text("Проформа не найдена.")
                context.user_data['delete_messages'].append(message.message_id)

        except Exception as e:
            message = await query.message.reply_text(f"Произошла ошибка при получении проформы: {str(e)}")
            context.user_data['delete_messages'].append(message.message_id)


def null_status(order_id):
    # Создаем подключение к базе данных
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    try:
        # Обновляем статус ордера
        logging.info(f"Updating order status for order_id: {order_id}")
        cursor.execute("UPDATE orders SET status = 0 WHERE order_id = ?",
                       (order_id,))
        conn.commit()

        logging.info(f"Order status updated for order_id: {order_id}")


    except Exception as e:
        logging.error(f"Failed to send order info to admin bot: {e}")
        print(f"Принт: Ошибка при отправке сообщения: {e}")

    finally:
        conn.close()
        logging.info(f"Database connection closed for order_id: {order_id}")

