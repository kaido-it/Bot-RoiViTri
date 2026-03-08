"""
User Service - Quản lý người dùng
"""
from typing import Optional
from datetime import datetime

from src.bot.database.db import get_db
import config


class UserService:
    """Service quản lý người dùng"""
    
    @staticmethod
    def create_user(telegram_id: int, username: str = None, full_name: str = None) -> bool:
        """Tạo user mới"""
        db = get_db()
        
        # Kiểm tra user đã tồn tại chưa
        existing = db.fetchone(
            "SELECT id FROM users WHERE telegram_id = ?",
            (telegram_id,)
        )
        
        if existing:
            return False
        
        db.execute(
            """
            INSERT INTO users (telegram_id, username, full_name)
            VALUES (?, ?, ?)
            """,
            (telegram_id, username, full_name)
        )
        return True
    
    @staticmethod
    def get_user(telegram_id: int) -> Optional[dict]:
        """Lấy thông tin user"""
        db = get_db()
        row = db.fetchone(
            "SELECT * FROM users WHERE telegram_id = ?",
            (telegram_id,)
        )
        
        if row:
            return dict(row)
        return None
    
    @staticmethod
    def get_user_by_id(user_id: int) -> Optional[dict]:
        """Lấy thông tin user theo ID"""
        db = get_db()
        row = db.fetchone(
            "SELECT * FROM users WHERE id = ?",
            (user_id,)
        )
        
        if row:
            return dict(row)
        return None
    
    @staticmethod
    def update_full_name(telegram_id: int, full_name: str) -> bool:
        """Cập nhật tên đầy đủ"""
        db = get_db()
        db.execute(
            "UPDATE users SET full_name = ? WHERE telegram_id = ?",
            (full_name, telegram_id)
        )
        return True
    
    @staticmethod
    def is_registered(telegram_id: int) -> bool:
        """Kiểm tra user đã đăng ký chưa"""
        db = get_db()
        row = db.fetchone(
            "SELECT id FROM users WHERE telegram_id = ? AND is_active = 1",
            (telegram_id,)
        )
        return row is not None
    
    @staticmethod
    def get_all_users() -> list:
        """Lấy danh sách tất cả user"""
        db = get_db()
        rows = db.fetchall("SELECT * FROM users WHERE is_active = 1")
        return [dict(row) for row in rows]
    
    @staticmethod
    def deactivate_user(telegram_id: int) -> bool:
        """Vô hiệu hóa user"""
        db = get_db()
        db.execute(
            "UPDATE users SET is_active = 0 WHERE telegram_id = ?",
            (telegram_id,)
        )
        return True
