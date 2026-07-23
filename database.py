import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

class DatabaseManager:
    def __init__(self):
        self.conn = psycopg2.connect(os.getenv("DATABASE_URL"))
        self.create_table()

    def create_table(self):
        with self.conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id BIGINT PRIMARY KEY,
                    first_name TEXT,
                    last_name TEXT,
                    language TEXT
                );
            """)
            self.conn.commit()

    def save_user(self, user_id, first_name, last_name, lang):
        with self.conn.cursor() as cur:
            cur.execute("""
                INSERT INTO users (user_id, first_name, last_name, language)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (user_id) DO UPDATE 
                SET first_name = EXCLUDED.first_name, 
                    last_name = EXCLUDED.last_name,
                    language = EXCLUDED.language;
            """, (user_id, first_name, last_name, lang))
            self.conn.commit()

    def get_user(self, user_id):
        with self.conn.cursor() as cur:
            cur.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
            return cur.fetchone()