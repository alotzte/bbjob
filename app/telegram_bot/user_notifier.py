import time
from telegram import Bot
import schedule
from db import connect_to_database
from config import Config

def send_greetings(bot, chat_id):
    current_time = time.strftime("%H:%M:%S", time.localtime())
    message = f"Привет! Текущее время: {current_time}"
    bot.send_message(chat_id, message)


def check_and_notify_users(bot):
    conn, cursor = connect_to_database()
    cursor.execute("SELECT user_id, telegram_id FROM users_test WHERE telegram_id <> 0")
    results = cursor.fetchall()
    conn.close()

    for user_id, telegram_id in results:
        send_greetings(bot, telegram_id)


def job():
    bot_token = Config.TOKEN
    bot = Bot(token=bot_token)
    check_and_notify_users(bot)


schedule.every(1).minutes.do(job)

if __name__ == "__main__":
    while True:
        schedule.run_pending()
        time.sleep(1)
