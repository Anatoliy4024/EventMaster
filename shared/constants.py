# constants.py

# constants.py

from telegram import InlineKeyboardMarkup, InlineKeyboardButton


ORDER_STATUS = {
    "1-не заполнено - невозможно выполнить расчет стоимости": 1,
    "2-заполнено для расчета": 2,
    "3-зарезервировано - заказчик оплатил аванс": 3,
    "4-Ирина и Сервисная служба получили сообщение о новой ПРОФОРМЕ": 4,
    "5-Заказчик зашел в АдминБот и просмотрел свою ПРОФОРМУ": 5,
    "55-Ирина зашла в АдминБот и просмотрела новую ПРОФОРМУ": 55
}

# Класс для хранения данных пользователя
class UserData:
    def __init__(self):
        self.language = None
        self.step = None

    def set_language(self, language):
        self.language = language

    def get_language(self):
        return self.language

    def set_step(self, step):
        self.step = step

    def get_step(self):
        return self.step

# Функция для отключения кнопок выбора языка
def disable_language_buttons(reply_markup):
    new_keyboard = []
    for row in reply_markup.inline_keyboard:
        new_row = []
        for button in row:
            # Делаем кнопку неактивной, присваивая ей callback_data='none'
            new_row.append(InlineKeyboardButton(button.text, callback_data='none'))
        new_keyboard.append(new_row)
    return InlineKeyboardMarkup(new_keyboard)

# Другие константы, функции и классы можно добавлять сюда
