import os
import psycopg
from dotenv import load_dotenv

load_dotenv()
conn_string = os.getenv("DATABASE_URL")

if not conn_string:
    raise ValueError("DATABASE_URL не найден")

with psycopg.connect(conn_string) as conn:
    with conn.cursor() as cur:
        cur.execute("SELECT version();")
        print(cur.fetchone()[0])
