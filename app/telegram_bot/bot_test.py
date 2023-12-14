import logging
import psycopg2
from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import Updater, CommandHandler, MessageHandler, ConversationHandler, CallbackContext, Filters

from config import Config

# Устанавливаем уровень логгирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Определение состояний для конечного автомата
START, LOGIN, REGISTER, ROLE, DEPARTMENT = range(5)

# Клавиатура для выбора роли
reply_keyboard = [['HR', 'Руководитель отдела']]

# Соединение с базой данных PostgreSQL
conn = psycopg2.connect(
    database=Config.DB_NAME,
    user=Config.DB_USER,
    password=Config.DB_PASSWORD,
    host=Config.DB_HOST,
    port=Config.DB_PORT
)
cursor = conn.cursor()

# Создание таблицы users, если она не существует
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users_test (
        user_id SERIAL PRIMARY KEY,
        first_name VARCHAR(50),
        last_name VARCHAR(50),
        middle_name VARCHAR(50),
        username VARCHAR(50),
        password VARCHAR(50),
        email VARCHAR(50),
        user_role VARCHAR(20),
        department_number INTEGER
    )
''')
conn.commit()

# Функция начала диалога
def start(update: Update, context: CallbackContext) -> int:
    update.message.reply_text(
        "Привет! Я твой бот. Давай начнем. У тебя уже есть аккаунт?",
        reply_markup=ReplyKeyboardMarkup([['Да', 'Нет']], one_time_keyboard=True),
    )

    return START

# Функция обработки ответа на вопрос о наличии аккаунта
def check_account(update: Update, context: CallbackContext) -> int:
    user_response = update.message.text.lower()
    if user_response == 'да':
        update.message.reply_text("Отлично! Давай войдем.")
        return LOGIN
    else:
        update.message.reply_text("Хорошо, давай создадим новый аккаунт. Введи свои данные.")
        return REGISTER

# Функция регистрации нового пользователя
def register(update: Update, context: CallbackContext) -> int:
    user_data = context.user_data
    user_data['first_name'] = update.message.text
    update.message.reply_text("Теперь введи свою фамилию:")
    return ROLE

# Функция обработки выбора роли
def select_role(update: Update, context: CallbackContext) -> int:
    user_data = context.user_data
    user_data['last_name'] = update.message.text

    update.message.reply_text(
        "Теперь введи свое отчество:"
    )
    return ROLE

# Функция завершения регистрации
def finish_registration(update: Update, context: CallbackContext) -> int:
    user_data = context.user_data
    user_data['middle_name'] = update.message.text

    update.message.reply_text(
        "Отлично! Теперь введи свой username:"
    )
    return ROLE

# Функция обработки выбора роли
def select_role(update: Update, context: CallbackContext) -> int:
    user_data = context.user_data
    user_data['username'] = update.message.text

    update.message.reply_text(
        "Теперь введи свой пароль:"
    )
    return ROLE

# Функция завершения регистрации
def finish_registration(update: Update, context: CallbackContext) -> int:
    user_data = context.user_data
    user_data['password'] = update.message.text

    update.message.reply_text(
        "Отлично! Теперь введи свой email:"
    )
    return ROLE

# Функция для обработки выбора роли
def select_role(update: Update, context: CallbackContext) -> int:
    user_data = context.user_data
    user_data['email'] = update.message.text

    update.message.reply_text(
        "Отлично! Теперь выбери свою роль:",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
    )
    return ROLE

# Функция обработки выбора роли
def select_role(update: Update, context: CallbackContext) -> int:
    user_data = context.user_data
    user_data['role'] = update.message.text

    if user_data['role'] == 'Руководитель отдела':
        update.message.reply_text(
            "Теперь введи номер своего отдела:"
        )
        return DEPARTMENT
    elif user_data['role'] == 'HR':
        # Если выбрана роль HR, сохраняем данные в базе данных
        save_user_data(user_data)
        update.message.reply_text("Регистрация завершена! Ты зарегистрирован как HR.")
        return ConversationHandler.END
    else:
        update.message.reply_text("Неверная роль. Попробуйте снова.")
        return ROLE

# Функция обработки ввода номера отдела
def enter_department(update: Update, context: CallbackContext) -> int:
    user_data = context.user_data
    user_data['department_number'] = int(update.message.text)

    # Сохраняем данные в базе данных
    save_user_data(user_data)
    update.message.reply_text("Регистрация завершена! Ты зарегистрирован как Руководитель отдела.")
    return ConversationHandler.END

# Функция для сохранения данных пользователя в базе данных
def save_user_data(user_data):
    cursor.execute('''
        INSERT INTO users_test (first_name, last_name, middle_name, username, password, email, role, department_number)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    ''', (
        user_data['first_name'], user_data['last_name'], user_data['middle_name'],
        user_data['username'], user_data['password'], user_data['email'], user_data['role'],
        user_data.get('department_number', None)
    ))
    conn.commit()

# Функция для входа в систему
def login(update: Update, context: CallbackContext) -> int:
    update.message.reply_text("Введите свой username:")
    return LOGIN

# Функция для обработки введенного логина
def enter_login(update: Update, context: CallbackContext) -> int:
    user_login = update.message.text
    context.user_data['username'] = user_login

    update.message.reply_text("Введите свой пароль:")
    return LOGIN

# Функция для завершения входа в систему
def finish_login(update: Update, context: CallbackContext) -> int:
    user_data = context.user_data
    user_data['password'] = update.message.text

    # Поиск пользователя в базе данных
    cursor.execute('SELECT * FROM users_test WHERE username = %s AND password = %s', (user_data['username'], user_data['password']))
    user = cursor.fetchone()

    if user:
        user_id = user[0]
        update.message.reply_text(f"Вход выполнен успешно! Твой user_id: {user_id}")
    else:
        update.message.reply_text("Неверный логин или пароль. Попробуйте снова.")

    return ConversationHandler.END

# Функция для отправки user_id раз в пять минут
def send_user_id(context: CallbackContext):
    cursor.execute('SELECT user_id FROM users_test WHERE username = %s', ('your_bot_username',))
    user = cursor.fetchone()

    if user:
        user_id = user[0]
        context.bot.send_message(chat_id=user_id, text=f"Твой user_id: {user_id}")

def main():
    # Токен вашего телеграм бота
    token = Config.TOKEN

    # Создаем объект Updater и передаем ему токен вашего бота
    updater = Updater(token, use_context=True)

    # Получаем из него диспетчер
    dp = updater.dispatcher

    # Создаем ConversationHandler и регистрируем его в диспетчере
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            START: [MessageHandler(Filters.regex('^Да$|^Нет$'), check_account),],
            REGISTER: [MessageHandler(Filters.text, register)],
            ROLE: [MessageHandler(Filters.regex('^(HR|Руководитель отдела)$'), select_role)],
            DEPARTMENT: [MessageHandler(Filters.text, enter_department)],
            LOGIN: [MessageHandler(Filters.regex('^[A-Za-z0-9_]+$'), enter_login)],
        },
        fallbacks=[CommandHandler('start', start)]
    )
    dp.add_handler(conv_handler)

    # Добавляем хендлеры для входа в систему
    dp.add_handler(CommandHandler('login', login))
    dp.add_handler(MessageHandler(Filters.text, finish_login))

    # Создаем задачу для отправки user_id раз в пять минут
    updater.job_queue.run_repeating(send_user_id, interval=300, first=0)

    # Запускаем бота
    updater.start_polling()

    # Останавливаем бота при нажатии Ctrl+C
    updater.idle()

if __name__ == '__main__':
    main()
