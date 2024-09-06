# bot/admin_bot/scenarios/admin_scenario.py

# admin_scenario.py

from telegram import Update
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

