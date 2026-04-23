import os
import psycopg
from psycopg.rows import dict_row
from dotenv import load_dotenv

# load_dotenv() ищет файл .env в текущей рабочей директории (корне)
load_dotenv()

class DBManager:
    def __init__(self):
        self.conn_info = os.getenv("DATABASE_URL")
        if not self.conn_info:
            raise ValueError("DATABASE_URL не найден! Проверь файл .env в корне проекта.")

    def get_unprocessed_events(self):
        # Используем менеджер контекста, чтобы не забывать закрывать соединения
        with psycopg.connect(self.conn_info, row_factory=dict_row) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT id, title, description FROM events WHERE tags IS NULL LIMIT 10")
                return cur.fetchall()

    def update_event_data(self, id, tags, embedding):
        with psycopg.connect(self.conn_info) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE events SET tags = %s, embedding = %s WHERE id = %s",
                    (tags, embedding, id)
                )
