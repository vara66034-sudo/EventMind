import os
import re
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
DUMP_FILE = BASE_DIR / "mydb_backup.sql"
NEXTVAL_SEQUENCE_RE = re.compile(r"nextval\('([^']+)'::regclass\)")
CREATE_TABLE_RE = re.compile(r"(CREATE TABLE [\s\S]*?;)")

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

RESET_POSTGRES_SEQUENCES_SQL = """
DO $$
DECLARE
    row_data record;
    max_id bigint;
BEGIN
    FOR row_data IN
        SELECT
            table_schema,
            table_name,
            column_name,
            substring(column_default from 'nextval\\(''([^'']+)''::regclass\\)') as sequence_name
        FROM information_schema.columns
        WHERE table_schema = 'public'
          AND column_default LIKE 'nextval(%'
    LOOP
        EXECUTE format(
            'SELECT COALESCE(MAX(%I), 0) FROM %I.%I',
            row_data.column_name,
            row_data.table_schema,
            row_data.table_name
        )
        INTO max_id;

        IF max_id > 0 THEN
            EXECUTE format(
                'SELECT setval(%L::regclass, %s, true)',
                row_data.sequence_name,
                max_id
            );
        ELSE
            EXECUTE format(
                'SELECT setval(%L::regclass, 1, false)',
                row_data.sequence_name
            );
        END IF;
    END LOOP;
END $$;
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

def load_dump_sql(dump_file=DUMP_FILE, use_pgvector=False):
    if not dump_file.exists():
        raise FileNotFoundError(f"Файл дампа не найден: {dump_file}")

    dump_sql = dump_file.read_text(encoding="utf-8")
    return prepare_dump_sql(dump_sql, use_pgvector=use_pgvector)

def prepare_dump_sql(dump_sql, use_pgvector=False):
    # В текущем дампе поле tags сохранено как ARRAY без типа элемента.
    # PostgreSQL требует конкретный тип массива.
    dump_sql = dump_sql.replace('"tags" ARRAY NULL', '"tags" text[] NULL')

    if not use_pgvector:
        dump_sql = dump_sql.replace('"embedding" vector(384) NULL', '"embedding" text NULL')

    return add_missing_sequence_statements(dump_sql)

def add_missing_sequence_statements(dump_sql):
    def add_sequences_before_create(match):
        create_table_sql = match.group(1)
        sequence_names = sorted(set(NEXTVAL_SEQUENCE_RE.findall(create_table_sql)))
        if not sequence_names:
            return create_table_sql

        create_sequences_sql = "\n".join(
            f"CREATE SEQUENCE IF NOT EXISTS {sequence_name};"
            for sequence_name in sequence_names
        )
        return f"{create_sequences_sql}\n{create_table_sql}"

    return CREATE_TABLE_RE.sub(add_sequences_before_create, dump_sql)

def pgvector_available(conn):
    try:
        with conn.cursor() as cur:
            cur.execute("CREATE EXTENSION IF NOT EXISTS vector")
        conn.commit()
        return True
    except Exception:
        conn.rollback()
        return False

def create_missing_sequences(cur, dump_sql):
    from psycopg2 import sql

    sequence_names = sorted(set(NEXTVAL_SEQUENCE_RE.findall(dump_sql)))

    for sequence_name in sequence_names:
        cur.execute(
            sql.SQL("CREATE SEQUENCE IF NOT EXISTS {}").format(
                sql.Identifier(*sequence_name.split("."))
            )
        )

def restore_postgres_dump(conn, dump_file=DUMP_FILE):
    use_pgvector = pgvector_available(conn)
    dump_sql = load_dump_sql(dump_file, use_pgvector=use_pgvector)

    with conn.cursor() as cur:
        cur.execute(dump_sql)
        cur.execute(RESET_POSTGRES_SEQUENCES_SQL)

    conn.commit()

def main():
    conn, db_type = get_connection()
    cur = conn.cursor()
    if db_type == "sqlite":
        cur.executescript(SQLITE_SCHEMA_SQL)
    else:
        cur.execute(POSTGRES_SCHEMA_SQL)
    conn.commit()
    cur.close()

    if db_type == "postgres":
        restore_postgres_dump(conn)
        print(f"Дамп успешно загружен из {DUMP_FILE}")
    else:
        print("Дамп mydb_backup.sql пропущен: он содержит PostgreSQL-синтаксис")

    conn.close()
    print(f"Таблицы успешно созданы в {db_type}")

if __name__ == "__main__":
    main()
