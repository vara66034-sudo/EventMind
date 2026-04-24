import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

schema_sql = """
CREATE TABLE IF NOT EXISTS events (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    event_date TIMESTAMP,
    description TEXT,
    location TEXT,
    tags TEXT[],
    source TEXT NOT NULL,
    source_url TEXT UNIQUE,
    image_url TEXT,
    raw_description TEXT,
    imported_to_odoo BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS user_interests (
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    interest TEXT NOT NULL
);
"""

def main():
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL не найден в .env")

    conn = psycopg2.connect(database_url)
    cur = conn.cursor()

    cur.execute(schema_sql)

    conn.commit()
    cur.close()
    conn.close()

    print("Таблицы успешно созданы в Neon")

if __name__ == "__main__":
    main()
