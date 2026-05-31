import os
from dotenv import load_dotenv

load_dotenv()

# PostgreSQL schema (original)
POSTGRES_SCHEMA_SQL = """
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

# SQLite schema (simplified, no array types)
SQLITE_SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    event_date TEXT,
    description TEXT,
    location TEXT,
    tags TEXT,
    source TEXT NOT NULL,
    source_url TEXT UNIQUE,
    image_url TEXT,
    raw_description TEXT,
    imported_to_odoo INTEGER DEFAULT 0,
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS user_interests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    interest TEXT NOT NULL
);
"""

def get_connection():
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL не найден в .env")
    if database_url.startswith("sqlite:///"):
        import sqlite3
        db_path = database_url.replace("sqlite:///", "")
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        return conn, "sqlite"
    else:
        import psycopg2
        conn = psycopg2.connect(database_url)
        return conn, "postgres"

def main():
    conn, db_type = get_connection()
    cur = conn.cursor()
    if db_type == "sqlite":
        cur.executescript(SQLITE_SCHEMA_SQL)
    else:
        cur.execute(POSTGRES_SCHEMA_SQL)
    conn.commit()
    cur.close()
    conn.close()
    print(f"Таблицы успешно созданы в {db_type}")

if __name__ == "__main__":
    main()
