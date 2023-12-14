import psycopg2
from telegram.error import NetworkError
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, ConversationHandler
from config import Config
from db import connect_to_database

TOKEN = Config.TOKEN

USERNAME, PASSWORD, AUTHENTICATED = range(3)


def check_user_authorization(context, user_id):
    conn, cursor = connect_to_database()
    cursor.execute(f"SELECT * FROM users_test WHERE telegram_id = {user_id}")
    result = cursor.fetchone()
    conn.close()
    return result


def stage_start(update: Update, context: CallbackContext) -> int:
    user_id = update.message.from_user.id
    if check_user_authorization(context, user_id):
        update.message.reply_text('Вы уже авторизованы!')
        return AUTHENTICATED
    else:
        update.message.reply_text('Добро пожаловать! Введите свой username:')
        return USERNAME


def stage_login(update: Update, context: CallbackContext) -> int:
    username = update.message.text
    user_id = update.message.from_user.id
    context.user_data['username'] = username
    context.user_data['telegram_id'] = user_id
    update.message.reply_text('Теперь введите пароль:')
    return PASSWORD


def stage_password(update: Update, context: CallbackContext) -> int:
    password = update.message.text
    username = context.user_data.get('username')
    telegram_id = context.user_data.get('telegram_id')

    if check_login_password(context, password, username):
        # Сохраняем информацию об авторизации в базе данных
        save_user_authorization(context, telegram_id, username)
        update.message.reply_text('Вы успешно авторизовались!')
    else:
        update.message.reply_text('Неверные учетные данные. Попробуйте еще раз.')

    return ConversationHandler.END


def save_user_authorization(context, telegram_id, username):
    print('GO SAVE')
    conn, cursor = connect_to_database()
    cursor.execute(
        f"UPDATE users_test SET telegram_id = '{telegram_id}', is_authorized = TRUE WHERE username = '{username}'")
    conn.commit()
    conn.close()


def check_login_password(context, password, username):
    conn, cursor = connect_to_database()
    cursor.execute(f"SELECT * FROM users_test WHERE username = '{username}' AND password = '{password}'")
    result = cursor.fetchone()
    conn.close()
    return result


def main() -> None:
    updater = Updater(TOKEN)
    dp = updater.dispatcher
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", stage_start)],
        states={
            USERNAME: [MessageHandler(Filters.text & ~Filters.command, stage_login)],
            PASSWORD: [MessageHandler(Filters.text & ~Filters.command, stage_password)],
            AUTHENTICATED: []
        },
        fallbacks=[],
    )

    dp.add_handler(conv_handler)
    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    try:
        main()
    except NetworkError:
        main()
