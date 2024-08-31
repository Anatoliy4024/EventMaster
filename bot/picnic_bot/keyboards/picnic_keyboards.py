# bot/picnic_bot/keyboards/picnic_keyboards.py

from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime, timedelta
import calendar

import logging

# ��������� �����������
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def to_superscript(num_str):
    """������������ ������ ���� � ����������� �����."""
    superscript_map = str.maketrans('0123456789', '??????????')
    return num_str.translate(superscript_map)


def generate_month_name(month, language):
    months = {
        'en': ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
    'ru': ["���", "���", "���", "���", "���", "���", "���", "���", "���", "���", "���", "���"],
    'es': ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"],
    'fr': ["Jan", "F?v", "Mar", "Avr", "Mai", "Juin", "Juil", "Ao?", "Sep", "Oct", "Nov", "D?c"],
    'uk': ["ѳ�", "���", "���", "��", "���", "���", "���", "���", "���", "���", "���", "���"],
    'pl': ["Sty", "Lut", "Mar", "Kwi", "Maj", "Cze", "Lip", "Sie", "Wrz", "Pa?", "Lis", "Gru"],
    'de': ["Jan", "Feb", "M?r", "Apr", "Mai", "Jun", "Jul", "Aug", "Sep", "Okt", "Nov", "Dez"],
    'it': ["Gen", "Feb", "Mar", "Apr", "Mag", "Giu", "Lug", "Ago", "Set", "Ott", "Nov", "Dic"]
    }
    return months[language][month - 1]


def generate_calendar_keyboard(month_offset=0, language='en'):
    today = datetime.today()
    base_month = today.month + month_offset
    base_year = today.year

    if base_month > 12:
        base_month -= 12
        base_year += 1
    elif base_month < 1:
        base_month += 12
        base_year -= 1

    first_of_month = datetime(base_year, base_month, 1)
    last_day = calendar.monthrange(first_of_month.year, first_of_month.month)[1]
    last_of_month = first_of_month.replace(day=last_day)

    month_name = generate_month_name(first_of_month.month, language)

    days_of_week = {
        'en': ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
        'ru': ["��", "��", "��", "��", "��", "��", "��"],
        'es': ["Lun", "Mar", "Mi?", "Jue", "Vie", "S?b", "Dom"],
        'fr': ["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"],
        'uk': ["��", "��", "��", "��", "��", "��", "��"],
        'pl': ["Pon", "Wt", "?r", "Czw", "Pi?", "Sob", "Niedz"],
        'de': ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"],
        'it': ["Lun", "Mar", "Mer", "Gio", "Ven", "Sab", "Dom"]
    }

    # ������� ��������� ������
    calendar_buttons = []

    # ��������� ��� ������ � ������ �������
    calendar_buttons = [[InlineKeyboardButton(day, callback_data='none')] for day in days_of_week[language]]

    start_weekday = first_of_month.weekday()
    current_date = first_of_month

    # ��������� ��������� ����� ������
    for _ in range(5):
        for day in range(len(calendar_buttons)):
            if current_date.day == 1 and day < start_weekday:
                calendar_buttons[day].append(InlineKeyboardButton(" ", callback_data='none'))
            elif current_date > last_of_month:
                calendar_buttons[day].append(InlineKeyboardButton(" ", callback_data='none'))
            else:
                if current_date <= today:
                    # ���������� to_superscript ��� �������������� ��� � ����������� �����
                    day_text = to_superscript(str(current_date.day))
                    calendar_buttons[day].append(InlineKeyboardButton(f"? {day_text}", callback_data='none'))
                else:
                    calendar_buttons[day].append(InlineKeyboardButton(f" {current_date.day}",
                                                                      callback_data=f'date_{current_date.strftime("%Y-%m-%d")}'))
                current_date += timedelta(days=1)

    prev_month_button = InlineKeyboardButton("<", callback_data=f"prev_month_{month_offset - 1}") if month_offset > -1 else InlineKeyboardButton(" ", callback_data="none")
    next_month_button = InlineKeyboardButton(">", callback_data=f"next_month_{month_offset + 1}") if month_offset < 2 else InlineKeyboardButton(" ", callback_data="none")
    month_name_button = InlineKeyboardButton(f"{month_name} {first_of_month.year}", callback_data="none")

    # ��������� ������ � ��������� ������ ����� �������� ������������ �������
    calendar_buttons.append([prev_month_button, month_name_button, next_month_button])

    return InlineKeyboardMarkup(calendar_buttons)
def generate_time_selection_keyboard(language, stage='start', start_time=None):
    start_time_dt = datetime.strptime('08:00', '%H:%M')
    end_time_dt = datetime.strptime('22:00', '%H:%M')

    time_buttons = []
    current_time = start_time_dt

    while current_time <= end_time_dt:
        time_str = current_time.strftime('%H:%M')
        if stage == 'end' and start_time:
            start_time_dt = datetime.strptime(start_time, '%H:%M')
            if current_time < start_time_dt + timedelta(hours=2):
                time_buttons.append(InlineKeyboardButton(f"? {time_str}", callback_data='none'))
            else:
                time_buttons.append(InlineKeyboardButton(f" {time_str}", callback_data=f'time_{time_str}'))
        else:
            if current_time >= datetime.strptime('20:30', '%H:%M'):
                time_buttons.append(InlineKeyboardButton(f"? {time_str}", callback_data='none'))
            else:
                time_buttons.append(InlineKeyboardButton(f" {time_str}", callback_data=f'time_{time_str}'))
        current_time += timedelta(minutes=30)

    num_buttons_per_row = 3
    rows = [time_buttons[i:i + num_buttons_per_row] for i in range(0, len(time_buttons), num_buttons_per_row)]

    time_selection_headers = {
        'start': {
            'en': 'Planning to start around...',
            'ru': '�������� ������ �...',
            'es': 'Planeo comenzar alrededor de...',
            'fr': 'Je pr?vois de commencer vers...',
            'uk': '������ ������ �...',
            'pl': 'Planuj? rozpocz?? oko?o...',
            'de': 'Ich plane zu beginnen um...',
            'it': 'Prevedo di iniziare intorno alle...'
        },
        'end': {
            'en': 'Planning to end around...',
            'ru': '�������� ��������� �����...',
            'es': 'Planeo terminar alrededor de...',
            'fr': 'Je pr?vois de terminer vers...',
            'uk': '������ �������� ��������� �...',
            'pl': 'Planuj? zako?czy? oko?o...',
            'de': 'Ich plane zu beenden um...',
            'it': 'Prevedo di finire intorno alle...'
        }
    }
    selection_text = time_selection_headers[stage].get(language, "Select start and end time (minimum duration 2 hours)")

    keyboard = [
        [InlineKeyboardButton(selection_text, callback_data='none')]
    ] + rows

    return InlineKeyboardMarkup(keyboard)


# # ������ ������ ������� � ����� ������� � �������� �������� � ������� � 5 �����
# from reserved_date import is_slot_available  # ���������, ��� ������������ ���������
#
# def generate_time_selection_keyboard(language, stage='start', start_time=None, date=None):
#     start_time_dt = datetime.strptime('08:00', '%H:%M')
#     end_time_dt = datetime.strptime('22:00', '%H:%M')
#
#     time_buttons = []
#     current_time = start_time_dt
#
#     while current_time <= end_time_dt:
#         time_str = current_time.strftime('%H:%M')
#
#         if stage == 'end' and start_time:
#             start_time_dt = datetime.strptime(start_time, '%H:%M')
#             if current_time < start_time_dt + timedelta(hours=2):
#                 time_buttons.append(InlineKeyboardButton(f"? {time_str}", callback_data='none'))
#             else:
#                 time_buttons.append(InlineKeyboardButton(f" {time_str}", callback_data=f'time_{time_str}'))
#         else:
#             # ��������� ����������� �����
#             if not is_slot_available(date, time_str, (current_time + timedelta(minutes=30)).strftime('%H:%M')):
#                 time_buttons.append(InlineKeyboardButton(f"? {time_str}", callback_data='none'))
#             else:
#                 time_buttons.append(InlineKeyboardButton(f" {time_str}", callback_data=f'time_{time_str}'))
#         current_time += timedelta(minutes=30)
#
#     num_buttons_per_row = 3
#     rows = [time_buttons[i:i + num_buttons_per_row] for i in range(0, len(time_buttons), num_buttons_per_row)]
#
#     time_selection_headers = {
#         'start': {
#             'en': 'Planning to start around...',
#             'ru': '�������� ������ �...',
#             'es': 'Planeo comenzar alrededor de...',
#             'fr': 'Je pr?vois de commencer vers...',
#             'uk': '������ ������ �...',
#             'pl': 'Planuj? rozpocz?? oko?o...',
#             'de': 'Ich plane zu beginnen um...',
#             'it': 'Prevedo di iniziare intorno alle...'
#         },
#         'end': {
#             'en': 'Planning to end around...',
#             'ru': '�������� ��������� �����...',
#             'es': 'Planeo terminar alrededor de...',
#             'fr': 'Je pr?vois de terminer vers...',
#             'uk': '������ �������� ��������� �...',
#             'pl': 'Planuj? zako?czy? oko?o...',
#             'de': 'Ich plane zu beenden um...',
#             'it': 'Prevedo di finire intorno alle...'
#         }
#     }
#     selection_text = time_selection_headers[stage].get(language, "Select start and end time (minimum duration 2 hours)")
#
#     keyboard = [
#         [InlineKeyboardButton(selection_text, callback_data='none')]
#     ] + rows
#
#     return InlineKeyboardMarkup(keyboard)
#
#





def language_selection_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("?? EN", callback_data='lang_en'),
            InlineKeyboardButton("?? ES", callback_data='lang_es'),
            InlineKeyboardButton("?? IT", callback_data='lang_it'),
            InlineKeyboardButton("?? FR", callback_data='lang_fr')
        ],
        [
            InlineKeyboardButton("?? UA", callback_data='lang_uk'),
            InlineKeyboardButton("?? PL", callback_data='lang_pl'),
            InlineKeyboardButton("?? DE", callback_data='lang_de'),
            InlineKeyboardButton("?? RU", callback_data='lang_ru')

        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def yes_no_keyboard(language):
    texts = {
        'en': {'yes': 'Yes', 'no': 'No'},
        'ru': {'yes': '��', 'no': '�����'},
        'es': {'yes': 'S?', 'no': 'No'},
        'fr': {'yes': 'Oui', 'no': 'Non'},
        'uk': {'yes': '���', 'no': '�����'},
        'pl': {'yes': 'Tak', 'no': 'Nie'},
        'de': {'yes': 'Ja', 'no': 'Nein'},
        'it': {'yes': 'S?', 'no': 'No'}
    }

    keyboard = [
        [
            InlineKeyboardButton(texts[language]['yes'], callback_data='yes'),
            InlineKeyboardButton(texts[language]['no'], callback_data='no')
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def generate_person_selection_keyboard(language):
    person_buttons = [InlineKeyboardButton(f" {i}", callback_data=f'person_{i}') for i in range(2, 22)]
    num_buttons_per_row = 5
    rows = [person_buttons[i:i + num_buttons_per_row] for i in range(0, len(person_buttons), num_buttons_per_row)]
    return InlineKeyboardMarkup(rows)

def generate_party_styles_keyboard(language):
    styles = {
        'en': [
            ("Corporate", "Breakfast on the beach"),
            ("Gender reveal", "Dinner by candlelight"),
            ("Romantic meeting", "Wedding anniversary"),
            ("Child's birthday", "Bachelorette party"),
            ("Adult's birthday", "Gift certificate")
        ],
        'ru': [
            ("��������", "������������� �������"),
            ("����������", "���������� ����������"),
            ("��������� ����", "�������� ���� ��������"),
            ("��������� �������", "������� ���� ��������"),
            ("���� ��� ������", "������� �� �����")
        ],
        'es': [
            ("Cena de empressa", "Cena a la luz de las velas"),
            ("Cumplea?os adulto", "Tarjeta de regalo"),
            ("Encuentro rom?ntico", "Desayuno en la playa"),
            ("Aniversario de bodas", "Despedida de soltera"),
            ("Revelaci?n de sexo", "Cumplea?os infantil")
        ],
        'fr': [
            ("Corporatif", "Enterrement de vie de jeune fille"),
            ("Certificat cadeau", "Petit d?jeuner sur la plage"),
            ("Anniversaire adulte", "Anniversaire de mariage"),
            ("R?v?lation de sexe", "D?ner aux chandelles"),
            ("Rencontre romantique", "Anniversaire d'enfant")        ],
        'uk': [
            ("����������", "�������� ���� ����������"),
            ("ĳ���-�����", "������������ ����������"),
            ("��������� ����", "������� ���� ����������"),
            ("г����� ������", "���������� ������"),
            ("������� �� ����", "������ ��� ������")        ],
        'pl': [
            ("Korporacyjny", "Kolacja przy ?wiecach"),
            ("Bon upominkowy", "Romantyczne spotkanie"),
            ("Rocznica ?lubu", "Dzieci?ce urodziny"),
            ("Ujawnienie p?ci", "?niadanie na pla?y"),
            ("Doros?e urodziny", "Wiecz?r panie?ski")
        ],
        'de': [
            ("Jubil?um", "Junggesellinnenabschied"),
            ("Firmenfeier", "Abendessen bei Kerzenschein"),
            ("Sternenabend", "Geschlechtsenth?llung"),
            ("Geschenkgutschein", "Romantisches Treffen"),
            ("Kindergeburtstag", "Fr?hst?ck am Strand")
        ],
        'it': [
            ("Corporativo", "Festa di addio al nubilato"),
            ("Incontro romantico", "Anniversario di matrimonio"),
            ("Certificato regalo", "Colazione sulla spiaggia"),
            ("Rivelazione del sesso", "Compleanno dell'adulto"),
            ("Cena a lume di candela", "Compleanno del bambino")
        ]
    }

    keyboard = []
    for style_pair in styles[language]:
        keyboard.append([InlineKeyboardButton(style_pair[0], callback_data=f'style_{style_pair[0].strip("? ")}'),
                         InlineKeyboardButton(style_pair[1], callback_data=f'style_{style_pair[1].strip("? ")}')])

    return InlineKeyboardMarkup(keyboard)