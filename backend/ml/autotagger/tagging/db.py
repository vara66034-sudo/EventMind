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

    def get_unprocessed_events(self, limit_val: int = 20):
        """Берем события для тестов (без учета tags IS NULL для перезаписи)"""
        with psycopg.connect(self.conn_info, row_factory=dict_row) as conn:
            with conn.cursor() as cur:
                # Используем %s для psycopg
                cur.execute("SELECT id, title, description FROM events LIMIT %s", (limit_val,))
                return cur.fetchall()

    def update_event_data(self, id: int, tags: list, embedding: list):
        """Обновляем данные события"""
        with psycopg.connect(self.conn_info) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE events 
                    SET tags = %s, 
                        embedding = %s 
                    WHERE id = %s
                    """,
                    (tags, embedding, id)
                )
            conn.commit()
