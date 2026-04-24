import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

def run_migration():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        print("Starting SQL migration...")
        
        # Add columns
        cur.execute("ALTER TABLE user_favorites ADD COLUMN IF NOT EXISTS event_start_date TIMESTAMP NULL;")
        cur.execute("ALTER TABLE user_favorites ADD COLUMN IF NOT EXISTS reminder_sent BOOLEAN DEFAULT FALSE;")
        
        # Delete duplicates before creating index
        cur.execute("""
            DELETE FROM user_favorites a 
            USING user_favorites b 
            WHERE a.id > b.id 
              AND a.user_id = b.user_id 
              AND a.event_id = b.event_id;
        """)
        
        # Create unique index
        cur.execute("CREATE UNIQUE INDEX IF NOT EXISTS uq_user_favorite ON user_favorites (user_id, event_id);")
        
        conn.commit()
        print("SQL migration completed successfully!")
        
    except Exception as e:
        print(f"Migration error: {e}")
    finally:
        if conn:
            cur.close()
            conn.close()

if __name__ == "__main__":
    run_migration()
