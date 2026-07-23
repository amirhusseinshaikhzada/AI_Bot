import os
import psycopg2
from psycopg2 import extras

class DatabaseManager:
    def __init__(self):
        # این آدرس را از تنظیمات Render (External Database URL) بردارید
        self.db_url = os.getenv("DATABASE_URL")
        if not self.db_url:
            raise Exception("DATABASE_URL environment variable is not set!")
        
        # Render گاهی اوقات از پروتکل postgres استفاده می‌کند در حالی که psycopg2 نیاز به postgresql دارد
        if self.db_url.startswith("postgres://"):
            self.db_url = self.db_url.replace("postgres://", "postgresql://", 1)
        
        self._create_tables()

    def _get_connection(self):
        return psycopg2.connect(self.db_url)

    def _create_tables(self):
        """ایجاد جداول در صورت عدم وجود"""
        query = """
        CREATE TABLE IF NOT EXISTS users (
            user_id BIGINT PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query)
            conn.commit()

    def get_user(self, user_id):
        """بررسی وجود کاربر در دیتابیس"""
        query = "SELECT * FROM users WHERE user_id = %s;"
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=extras.DictCursor) as cur:
                cur.execute(query, (user_id,))
                return cur.fetchone()

    def add_user(self, user_id, username, first_name):
        """ثبت کاربر جدید"""
        query = """
        INSERT INTO users (user_id, username, first_name) 
        VALUES (%s, %s, %s) 
        ON CONFLICT (user_id) DO NOTHING;
        """
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (user_id, username, first_name))
            conn.commit()

# نمونه‌سازی از کلاس برای استفاده در بقیه فایل‌ها
db = DatabaseManager()
