import os
import json
import psycopg2
from psycopg2.extras import execute_batch
from dotenv import load_dotenv

load_dotenv()

# Берем ссылку на базу данных из скрытого окружения (или из секретов GitHub)
DATABASE_URL = os.getenv("DATABASE_URL")
JSON_FILE = "telegram_events.json"

def upload_to_neon():
    if not DATABASE_URL:
        print("❌ Ошибка: Не найден DATABASE_URL. Проверьте секреты или файл .env")
        return

    if not os.path.exists(JSON_FILE):
        print(f"❌ Ошибка: Файл {JSON_FILE} не найден. Сначала должен отработать парсер!")
        return

    # Читаем готовые данные из файла
    with open(JSON_FILE, "r", encoding="utf-8") as f:
        events = json.load(f)

    if not events:
        print("В файле нет данных для загрузки.")
        return

    print(f"Подключение к базе данных Neon... (Готовим к отправке {len(events)} событий)")

    try:
        # Подключаемся к PostgreSQL
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()

        # SQL-запрос для вставки данных
        # ON CONFLICT DO NOTHING защищает нас от дубликатов в базе
        insert_query = """
            INSERT INTO events (source, source_url, title, description, location, event_date, is_online, image_url, raw_description)
            VALUES (%(source)s, %(source_url)s, %(title)s, %(description)s, %(location)s, %(event_date)s, %(is_online)s, %(image_url)s, %(raw_description)s)
            ON CONFLICT (source_url) DO NOTHING;
        """

        # Быстрая массовая загрузка всех событий разом
        execute_batch(cursor, insert_query, events)
        conn.commit()
        
        print("🎉 Успешно! Данные из Телеграма загружены в облако Neon.")

    except Exception as e:
        print(f"⚠️ Ошибка при работе с базой данных: {e}")
    finally:
        # Всегда закрываем соединение
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()
            print("Соединение с базой закрыто.")

if __name__ == "__main__":
    upload_to_neon()
