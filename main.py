import telebot
from telebot import types
# 'email google bota: servic-bot@my-bot-347718.iam.gserviceaccount.com'
import os.path
from googleapiclient.discovery import build
from google.oauth2 import service_account

bot = telebot.TeleBot("5398982081:AAEYawaHSZbt2n3JARjau2zhPzlUKqtt34E")# Токен телеграмм бота
#777217637
avt_id = '' # id авторизующегося человека
avt_chat_id = '' # id чата с запросом авторизации
name = '' # имя авторизующегося человека
admin_id = '230932584' # id админа
ids = [230932584, 777217637]
# обработка авторизации
@bot.message_handler(commands=['avt'])
def get_avt(message):
    global avt_chat_id
    avt_chat_id = message.chat.id
    if message.from_user.id not in ids:
        bot.send_message(avt_chat_id, 'Введи свои ФИО и дождитесь ответа администратора')
        bot.register_next_step_handler(message, get_name)

def get_name(message):
    global name
    global avt_id
    avt_id = message.from_user.id
    name = message.text
# Создаем кнопки
    keyboard = types.InlineKeyboardMarkup()
    key_append = types.InlineKeyboardButton(text='Разрешить доступ', callback_data='yes')
    keyboard.add(key_append)
    key_exit = types.InlineKeyboardButton(text='Запретить доступ', callback_data='no')
    keyboard.add(key_exit)

    bot.send_message(admin_id, message.text)
    bot.send_message(admin_id, message.from_user.id, reply_markup=keyboard)

# Обработчик кнопок
@bot.callback_query_handler(func=lambda call: True)
def callback_worker (call):
    global ids
    global avt_id
    if call.data == 'yes':
        ids.append(avt_id)
        bot.send_message(admin_id, 'Пользователь добавлен на одну сессию')
        bot.send_message(avt_chat_id, 'Вы авторизованы, введите /start')
    if call.data == 'no':
        bot.send_message(admin_id, 'Запрос откланен')
        bot.send_message(avt_chat_id, 'Доступ запрещен!')
# Обработка команды старт
@bot.message_handler(commands=['start'])
def send_welcome(message):
    if message.from_user.id not in ids:
        print(ids, message.from_user.id)
        bot.send_message(message.chat.id, 'В доступе отказано! для запроса авторизации введи команду /avt')
    else:
        bot.send_message(message.chat.id, 'Введи фамилию либо имя либо дату рождения!')
# Работа с гугл таблицей
        @bot.message_handler(func=lambda message: True)
        def handle_text(message):
            # readonly разрешает только чтение таблицы(удалить для получения полного доступа)'
            SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
            base_dir = os.path.dirname(os.path.abspath(__file__))
            SERVICE_ACCOUNT_FILE = os.path.join(base_dir, 'credentials.json')

            credentials = service_account.Credentials.from_service_account_file(
                SERVICE_ACCOUNT_FILE, scopes=SCOPES)

            # указываем адрес листа и его название
            SAMPLE_SPREADSHEET_ID = '1fk8V9nHhG5BZ3vjgrqZkXxZFk-BMFeqwN8wqj45QyGU'
            SAMPLE_RANGE_NAME = 'Sheet1'

            service = build('sheets', 'v4', credentials=credentials)

            # Call the Sheets API
            sheet = service.spreadsheets()
            result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                        range=SAMPLE_RANGE_NAME).execute()
            values = result.get('values', [])
            val = values[:]
            name = message.text
            space_name = name.strip()
            print(name)
            serch = []
            for res in val:
                if space_name.title() in res:
                    serch += res
            if serch != []:
                bot.reply_to(message, str(serch))
            else:
                bot.reply_to(message, 'Искомый запрос не найден')



bot.infinity_polling()