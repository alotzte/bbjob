import psycopg2
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, ConversationHandler
from config import Config

TOKEN = Config.TOKEN

USERNAME, PASSWORD = range(2)


def stage_start(update: Update, context: CallbackContext) -> int:
    print("Step: start")
    update.message.reply_text('Добро пожаловать! Введите свой username:')
    return USERNAME


def stage_login(update: Update, context: CallbackContext) -> int:
    print("Step: login")
    username = update.message.text
    context.user_data['username'] = username
    update.message.reply_text('Теперь введите пароль:')
    return PASSWORD


def stage_password(update: Update, context: CallbackContext) -> int:
    print("Step: password")
    password = update.message.text
    username = context.user_data.get('username')

    if check_login_password(context, password, update, username):
        update.message.reply_text('Вы успешно авторизовались!')
        context.user_data.clear()
    else:
        update.message.reply_text('Неверные учетные данные. Попробуйте еще раз.')

    return ConversationHandler.END


def check_login_password(context, password, update, username):
    conn, cursor = connect_to_database()
    cursor.execute(f"SELECT * FROM users_test WHERE username = '{username}' AND password = '{password}'")
    result = cursor.fetchone()
    conn.close()
    return result


def connect_to_database():
    conn = psycopg2.connect(
        database=Config.DB_NAME,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        host=Config.DB_HOST,
        port=Config.DB_PORT
    )
    cursor = conn.cursor()
    return conn, cursor

def main() -> None:
    updater = Updater(TOKEN)
    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", stage_start)],
        states={
            USERNAME: [MessageHandler(Filters.text & ~Filters.command, stage_login)],
            PASSWORD: [MessageHandler(Filters.text & ~Filters.command, stage_password)],
        },
        fallbacks=[],
    )

    dp.add_handler(conv_handler)

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
