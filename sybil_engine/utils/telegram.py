import telebot

from sybil_engine.utils.utils import ConfigurationException

telegram_api_key = None
telegram_api_chat_id = None


def send_to_bot(msg):
    if telegram_api_key is None or telegram_api_chat_id is None:
        raise ConfigurationException('telegram api key and chat id should be configured if telegram is on')
    try:
        bot = telebot.TeleBot(telegram_api_key)
        bot.send_message(telegram_api_chat_id, msg)
    except Exception as error:
        print(f"Fail to send {msg}")
        print(error)


def set_telegram_api_chat_id(value):
    global telegram_api_chat_id
    telegram_api_chat_id = value


def set_telegram_api_key(value):
    global telegram_api_key
    telegram_api_key = value
