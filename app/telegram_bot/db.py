from config import Config
import psycopg2


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


class DB:
    pass
