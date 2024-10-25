
import configparser
import os
from datetime import datetime
import telebot
from telebot import types
from add_text import add_caption

def get_settings():
    """Читаем данные из конфигурационного файла."""
    config = configparser.ConfigParser()
    config.read("settings.ini")
    return (
        config["TELEGRAM"]["token_tg"],
        config["PATH"]["directory_path"],
        config["PUBLIC"]["public"],
    )

def get_latest_photo(directory):
    create_directory_if_not_exists(directory)
    """Возвращает путь к последнему обновленному изображению в директории."""
    files = [
        f for f in os.listdir(directory) 
        if os.path.isfile(os.path.join(directory, f)) and f.endswith(('.jpg', '.jpeg', '.png'))
    ]

    if not files:
        return None

    full_paths = [os.path.join(directory, f) for f in files]
    return max(full_paths, key=os.path.getmtime)

def format_file_name(dt, user_id):
    """Генерация имени файла с учетом даты и времени."""
    return f"{dt.year}-{dt.month:02d}-{dt.day:02d}-{dt.hour:02d}-{dt.minute:02d}_{user_id}.jpg"

def create_directory_if_not_exists(directory):
    """Создает директорию, если она не существует."""
    if not os.path.exists(directory):
        os.makedirs(directory)

def initialize_bot():
    """Инициализация бота."""
    token_tg, directory_path, public = get_settings()
    bot = telebot.TeleBot(token_tg)
    return bot, directory_path, public

bot, directory_path, public = initialize_bot()

@bot.message_handler(commands=["start"])
def start_message(message):
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add(types.KeyboardButton("Правила"), types.KeyboardButton("Начать"))
    
    bot.send_message(
        message.chat.id,
        f"Добро пожаловать, {message.from_user.first_name}!\n✨ Я - <b>{bot.get_me().first_name}</b>\n\n📸 Жду ваших фотографий!",
        parse_mode="html",
        reply_markup=markup,
    )

@bot.message_handler(content_types=["photo"])
def download_photo(message):
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add(types.KeyboardButton("Да"), types.KeyboardButton("Нет"))
    
    try:
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        create_directory_if_not_exists(directory_path)
        user_id = message.from_user.id
        dt = datetime.utcfromtimestamp(message.date)
        file_name = format_file_name(dt, user_id)
        file_path = os.path.join(directory_path, file_name)

        with open(file_path, "wb") as new_file:
            new_file.write(downloaded_file)

        latest_file = get_latest_photo(directory_path)
        add_caption(latest_file, 'captions.txt')
        bot.reply_to(message, 'Сохранили. Отправить её на канал?', reply_markup=markup)
        
    except telebot.exceptions.TelegramAPIError as e:
        bot.reply_to(message, f'Ошибка в Telegram API: {str(e)}')
    except Exception as e:
        bot.reply_to(message, f'Произошла ошибка: {str(e)}')

@bot.message_handler(content_types=["text"])
def send_photo(message):
    if message.text.lower() == 'правила':
        bot.send_message(
        message.chat.id,
        "👋 Здравствуйте!\n\n"
        '- Отправьте боту фотографию (можно отправить .jpg, .jpeg или .png файл).\n'
        "- Бот добавит на изображение приятную подпись\n"
        "- Бот спросит, хотите ли вы отправить его на канал или пользователю.\n"
        "- Нажмите 'Да' или ответьте вручную, если хотите отправить изображение"
        "- Чтобы остановить взаимодействие с ботом, просто прекратите отправлять команды или закройте чат.\n\n",
    )
    latest_photo = get_latest_photo(directory_path)
    
    if message.text.lower() == "да":
        if latest_photo:

            with open(latest_photo, 'rb') as photo:

                sent_message = bot.send_photo(message.chat.id, photo=photo)
                bot.forward_message(public, message.chat.id, sent_message.message_id)
                bot.send_message(message.chat.id, "Фото отправлено в группу!")
        
                start_message(message)
        else:
            bot.reply_to(message, 'Нет доступных фотографий для отправки.')        
    else:
        bot.send_message(message.chat.id, "Ждём другие фотографии...")
        start_message(message)
  

if __name__ == "__main__":
    print("Bot is running")
    bot.polling(none_stop=True)
