"""
Database connection and initialization for SQLite
"""
import sqlite3
from pathlib import Path
from typing import Optional
from contextlib import contextmanager

import config


class Database:
    """Lớp quản lý kết nối SQLite"""
    
    _instance: Optional['Database'] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._connection = None
        return cls._instance
    
    def __init__(self):
        if self._connection is None:
            self._init_database()
    
    def _init_database(self):
        """Khởi tạo database và các bảng"""
        # Tạo thư mục data nếu chưa tồn tại
        db_path = Path(config.DATABASE_CONFIG["path"])
        db_path.parent.mkdir(parents=True, exist_ok=True)
        
        self._connection = sqlite3.connect(
            config.DATABASE_CONFIG["path"],
            check_same_thread=False
        )
        self._connection.row_factory = sqlite3.Row
        
        # Tạo các bảng
        self._create_tables()
    
    def _create_tables(self):
        """Tạo các bảng trong database"""
        cursor = self._connection.cursor()
        
        # Bảng users
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id BIGINT UNIQUE NOT NULL,
                username TEXT,
                full_name TEXT,
                role TEXT DEFAULT 'user',
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Bảng attendance_records
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS attendance_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                action_type TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                note TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        
        # Bảng daily_summaries
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS daily_summaries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                date DATE NOT NULL,
                check_in_time TIMESTAMP,
                check_out_time TIMESTAMP,
                total_work_minutes INTEGER DEFAULT 0,
                break_minutes INTEGER DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users (id),
                UNIQUE(user_id, date)
            )
        """)
        
        self._connection.commit()
    
    @contextmanager
    def get_cursor(self):
        """Context manager để lấy cursor"""
        cursor = self._connection.cursor()
        try:
            yield cursor
            self._connection.commit()
        except Exception as e:
            self._connection.rollback()
            raise e
    
    def execute(self, query: str, params: tuple = ()):
        """Thực thi query và trả về cursor"""
        cursor = self._connection.cursor()
        cursor.execute(query, params)
        self._connection.commit()
        return cursor
    
    def fetchone(self, query: str, params: tuple = ()):
        """Thực thi query và lấy 1 row"""
        cursor = self._connection.cursor()
        cursor.execute(query, params)
        return cursor.fetchone()
    
    def fetchall(self, query: str, params: tuple = ()):
        """Thực thi query và lấy tất cả rows"""
        cursor = self._connection.cursor()
        cursor.execute(query, params)
        return cursor.fetchall()
    
    def close(self):
        """Đóng kết nối"""
        if self._connection:
            self._connection.close()


# Singleton instance
db = Database()


def get_db() -> Database:
    """Lấy instance của database"""
    return db
