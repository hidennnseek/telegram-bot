import os
import telebot
import logging
import time
from random import choice
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

# Проверка наличия библиотеки schedule
try:
    import schedule
except ImportError:
    print("Библиотека 'schedule' не установлена. Установите её с помощью команды: pip install schedule")
    exit(1)

# Укажите ваш токен здесь через переменную окружения
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '7814161895:AAECBrxkI8tB_KqU5j9b_MBJgncdhODWf3c')

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Создаем экземпляр бота
bot = telebot.TeleBot(TOKEN)

# Список имён игроков
players = ["Дима", "Андрюха", "Миха", "Сёма", "Диня", "Миша", "Мотик"]

# Список всех возможных челленджей
challenges = [
    "Снять майку и 20 раз отжаться",
    "Выпить 2 шота водки",
    "Выпить стакан пива залпом",
    "Поменятся одеждой полностью с соседом слева (трусы не включая) до следующего челленджа",
    "Каждый смешивает в стакан свой любимый алкоголь, а ты пьешь",
    "Придумать анекдот используя слова которые назовут другие участники (по 1 слову от каждого)",
    "Продай что нибудь какому нибудь рандому",
    "Рерролл и делай этот челлендж без рук",
    "СпетьКрикнуть «аааааауууууф»",
    "Выпить бокал пива через трубочку",
    "Разливать напитки для всех до следующего челленджа",
    "Произнести тост",
    "Армрестлинг с человеком слева",
    "Дегустация: с закрытыми глазами угадать все напитки, которые есть на столе / в досягаемости",
    "Организовать совместное фото со всеми участниками мальчишника"
]

# Словарь для хранения выполненных челленджей для каждого игрока
completed_challenges = {player: [] for player in players}

# Функция для выбора случайного челленджа для игрока
def get_random_challenge(player):
    available_challenges = [ch for ch in challenges if ch not in completed_challenges[player]]
    if not available_challenges:
        return "Нет доступных челленджей!"
    challenge = choice(available_challenges)
    completed_challenges[player].append(challenge)
    return challenge

# Функция для отправки челленджей всем игрокам
def send_challenges():
    for player in players:
        challenge = get_random_challenge(player)
        bot.send_message(chat_id, f"{player}, ты должен {challenge}", reply_markup=create_reroll_button(player))

# Запуск ежечасной отправки
schedule.every().hour.do(send_challenges)

# Функция для запуска расписания
def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)

# Создаем клавиатуру с кнопками "Старт" и "Перезагрузить бота"
def create_main_keyboard():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = KeyboardButton("Старт")
    button2 = KeyboardButton("Перезагрузить бота")
    markup.add(button1, button2)
    return markup

# Создаем inline-кнопку "Реролл"
def create_reroll_button(player):
    markup = InlineKeyboardMarkup()
    button = InlineKeyboardButton("Реролл", callback_data=f"reroll_{player}")
    markup.add(button)
    return markup

# Обработка команды /start
@bot.message_handler(commands=['start'])
def start(message):
    global chat_id
    chat_id = message.chat.id
    bot.send_message(chat_id, "Нажмите кнопку, чтобы начать игру!", reply_markup=create_main_keyboard())

# Обработка текстовых сообщений
@bot.message_handler(func=lambda message: True)
def handle_text(message):
    global chat_id
    chat_id = message.chat.id

    if message.text == "Старт":
        bot.send_message(chat_id, "Игра началась! Каждый час вы будете получать новые челленджи.")
        send_challenges()  # Отправляем первую порцию челленджей
        run_scheduler()
    elif message.text == "Перезагрузить бота":
        global completed_challenges
        # Сбрасываем выполненные челленджи
        completed_challenges = {player: [] for player in players}
        # Останавливаем текущий schedule
        schedule.clear()
        # Запускаем schedule заново
        run_scheduler()
        # Отправляем новое сообщение с кнопкой "Старт"
        bot.send_message(chat_id, "Бот перезагружен. Нажмите кнопку, чтобы начать игру!", reply_markup=create_main_keyboard())
    else:
        bot.send_message(chat_id, "Используйте кнопки ниже для управления ботом.")

# Обработка нажатия на кнопку "Реролл"
@bot.callback_query_handler(func=lambda call: call.data.startswith("reroll_"))
def reroll_challenge(call):
    player = call.data.split("_")[1]
    challenge = get_random_challenge(player)
    bot.send_message(call.message.chat.id, f"{player}, ваш новый челлендж: {challenge}", reply_markup=create_reroll_button(player))

# Запуск бота
if __name__ == "__main__":
    try:
        logger.info("Бот запущен.")
        bot.polling(none_stop=True)
    except KeyboardInterrupt:
        logger.info("Бот остановлен.")
    except Exception as e:
        logger.error(f"Произошла ошибка: {e}")
