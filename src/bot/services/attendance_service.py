"""
Attendance Service - Xử lý logic chấm công
"""
from typing import Optional, List
from datetime import datetime, date, timedelta
from datetime import datetime as dt

from src.bot.database.db import get_db
from src.bot.services import user_service
import config


class AttendanceService:
    """Service xử lý chấm công"""
    
    @staticmethod
    def has_checked_in_today(telegram_id: int) -> bool:
        """Kiểm tra đã check-in hôm nay chưa"""
        db = get_db()
        
        user = user_service.UserService.get_user(telegram_id)
        if not user:
            return False
        
        user_id = user["id"]
        today = date.today()
        
        row = db.fetchone(
            """
            SELECT id FROM attendance_records 
            WHERE user_id = ? AND action_type = ? AND DATE(timestamp) = ?
            """,
            (user_id, config.ACTION_CHECK_IN, today)
        )
        
        return row is not None
    
    @staticmethod
    def is_on_break(telegram_id: int) -> bool:
        """Kiểm tra đang trong giờ nghỉ"""
        db = get_db()
        
        user = user_service.UserService.get_user(telegram_id)
        if not user:
            return False
        
        user_id = user["id"]
        today = date.today()
        
        # Kiểm tra có break_start nhưng chưa có break_end
        break_start = db.fetchone(
            """
            SELECT id FROM attendance_records 
            WHERE user_id = ? AND action_type = ? AND DATE(timestamp) = ?
            """,
            (user_id, config.ACTION_BREAK_START, today)
        )
        
        if not break_start:
            return False
        
        # Kiểm tra có break_end sau break_start gần nhất chưa
        break_end = db.fetchone(
            """
            SELECT id FROM attendance_records 
            WHERE user_id = ? AND action_type = ? AND DATE(timestamp) = ? 
            AND timestamp > (SELECT MAX(timestamp) FROM attendance_records 
                           WHERE user_id = ? AND action_type = ? AND DATE(timestamp) = ?)
            """,
            (user_id, config.ACTION_BREAK_END, today, user_id, config.ACTION_BREAK_START, today)
        )
        
        return break_end is None
    
    @staticmethod
    def record_action(telegram_id: int, action_type: str, note: str = None) -> dict:
        """
        Ghi nhận một hành động chấm công
        Trả về dict với thông tin kết quả
        """
        db = get_db()
        
        # Lấy user
        user = user_service.UserService.get_user(telegram_id)
        if not user:
            return {
                "success": False,
                "message": "Ban chua dang ky! Vui long dung /start de dang ky."
            }
        
        user_id = user["id"]
        
        # Kiểm tra action hợp lệ
        if action_type == config.ACTION_CHECK_IN:
            # Kiểm tra đã check-in hôm nay chưa
            today = date.today()
            existing = db.fetchone(
                """
                SELECT id FROM attendance_records 
                WHERE user_id = ? AND action_type = ? AND DATE(timestamp) = ?
                """,
                (user_id, config.ACTION_CHECK_IN, today)
            )
            if existing:
                return {
                    "success": False,
                    "message": "Ban da bao len ca hom nay roi!"
                }
        
        elif action_type == config.ACTION_CHECK_OUT:
            # Kiểm tra đã check-in chưa
            today = date.today()
            check_in = db.fetchone(
                """
                SELECT id FROM attendance_records 
                WHERE user_id = ? AND action_type = ? AND DATE(timestamp) = ?
                """,
                (user_id, config.ACTION_CHECK_IN, today)
            )
            if not check_in:
                return {
                    "success": False,
                    "message": "Ban chua bao len ca hom nay!"
                }
            
            # Kiểm tra đã check-out chưa
            existing = db.fetchone(
                """
                SELECT id FROM attendance_records 
                WHERE user_id = ? AND action_type = ? AND DATE(timestamp) = ?
                """,
                (user_id, config.ACTION_CHECK_OUT, today)
            )
            if existing:
                return {
                    "success": False,
                    "message": "Ban da roi vi tri hom nay roi!"
                }
        
        elif action_type == config.ACTION_BREAK_START:
            # Kiểm tra đã check-in chưa
            if not AttendanceService.has_checked_in_today(telegram_id):
                return {
                    "success": False,
                    "message": "Ban chua bao len ca hom nay!"
                }
            
            # Kiểm tra đang trong giờ nghỉ chưa
            if AttendanceService.is_on_break(telegram_id):
                return {
                    "success": False,
                    "message": "Ban dang trong gio nghi! Vui long quay lai lam viec."
                }
        
        elif action_type == config.ACTION_BREAK_END:
            # Kiểm tra đang trong giờ nghỉ không
            if not AttendanceService.is_on_break(telegram_id):
                return {
                    "success": False,
                    "message": "Ban khong trong gio nghi!"
                }
        
        # Ghi nhận action
        now = datetime.now()
        db.execute(
            """
            INSERT INTO attendance_records (user_id, action_type, timestamp, note)
            VALUES (?, ?, ?, ?)
            """,
            (user_id, action_type, now, note)
        )
        
        # Cập nhật daily summary
        AttendanceService._update_daily_summary(user_id)
        
        # Tạo thông báo
        time_str = now.strftime("%H:%M:%S")
        message = AttendanceService._get_action_message(action_type, time_str, note)
        
        # Nếu là checkout, tính tổng thời gian làm việc
        if action_type == config.ACTION_CHECK_OUT:
            work_minutes = AttendanceService._get_today_work_minutes(user_id)
            hours = work_minutes // 60
            minutes = work_minutes % 60
            message += f"\nTong thoi gian lam viec: {hours}h {minutes}p"
        
        return {
            "success": True,
            "message": message,
            "timestamp": now
        }
    
    @staticmethod
    def _update_daily_summary(user_id: int):
        """Cập nhật daily summary"""
        db = get_db()
        today = date.today()
        
        # Lấy các action trong ngày
        records = db.fetchall(
            """
            SELECT action_type, timestamp FROM attendance_records
            WHERE user_id = ? AND DATE(timestamp) = ?
            ORDER BY timestamp ASC
            """,
            (user_id, today)
        )
        
        if not records:
            return
        
        # Tìm check-in và check-out
        check_in = None
        check_out = None
        break_start = None
        break_end = None
        
        for record in records:
            action = record["action_type"]
            timestamp = dt.fromisoformat(record["timestamp"])
            
            if action == config.ACTION_CHECK_IN and not check_in:
                check_in = timestamp
            elif action == config.ACTION_CHECK_OUT:
                check_out = timestamp
            elif action == config.ACTION_BREAK_START and not break_start:
                break_start = timestamp
            elif action == config.ACTION_BREAK_END:
                break_end = timestamp
        
        # Tính tổng thời gian làm việc
        total_minutes = 0
        if check_in and check_out:
            total_minutes = int((check_out - check_in).total_seconds() / 60)
        
        # Tính thời gian nghỉ
        break_minutes = 0
        if break_start and break_end:
            break_minutes = int((break_end - break_start).total_seconds() / 60)
        
        # Cập nhật hoặc insert
        db.execute(
            """
            INSERT INTO daily_summaries (user_id, date, check_in_time, check_out_time, total_work_minutes, break_minutes)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(user_id, date) DO UPDATE SET
                check_in_time = COALESCE(excluded.check_in_time, check_in_time),
                check_out_time = COALESCE(excluded.check_out_time, check_out_time),
                total_work_minutes = excluded.total_work_minutes,
                break_minutes = excluded.break_minutes
            """,
            (user_id, today, check_in, check_out, total_minutes - break_minutes, break_minutes)
        )
    
    @staticmethod
    def _get_today_work_minutes(user_id: int) -> int:
        """Lấy tổng thời gian làm việc hôm nay (phút)"""
        db = get_db()
        today = date.today()
        
        row = db.fetchone(
            "SELECT total_work_minutes FROM daily_summaries WHERE user_id = ? AND date = ?",
            (user_id, today)
        )
        
        if row:
            return row["total_work_minutes"] or 0
        return 0
    
    @staticmethod
    def _get_action_message(action_type: str, time_str: str, note: str = None) -> str:
        """Tạo thông báo cho từng action"""
        note_msg = f" - {note}" if note else ""
        
        messages = {
            config.ACTION_CHECK_IN: f"Ban da bao len ca luc {time_str}\nThoi gian lam viec bat dau duoc ghi nhan!",
            config.ACTION_BREAK_START: f"Ban da ra ca luc {time_str}\nThoi gian nghi duoc ghi nhan!{note_msg}",
            config.ACTION_BREAK_END: f"Ban da vao ca luc {time_str}\nTiep tuc lam viec nhe!",
            config.ACTION_CHECK_OUT: f"Ban da roi vi tri luc {time_str}{note_msg}\nHen gap lai!"
        }
        return messages.get(action_type, "Hanh dong duoc ghi nhan!")
    
    @staticmethod
    def get_today_history(telegram_id: int) -> dict:
        """Lấy lịch sử chấm công hôm nay"""
        db = get_db()
        
        user = user_service.UserService.get_user(telegram_id)
        if not user:
            return {
                "success": False,
                "message": "Ban chua dang ky!"
            }
        
        user_id = user["id"]
        today = date.today()
        
        records = db.fetchall(
            """
            SELECT action_type, timestamp, note FROM attendance_records
            WHERE user_id = ? AND DATE(timestamp) = ?
            ORDER BY timestamp ASC
            """,
            (user_id, today)
        )
        
        if not records:
            return {
                "success": True,
                "message": "Lich su cham cong hom nay:\n\nChua co ban ghi nao!",
                "records": []
            }
        
        # Tạo danh sách records
        record_list = []
        history_text = "Lich su cham cong hom nay:\n\n"
        
        for record in records:
            timestamp = dt.fromisoformat(record["timestamp"])
            time_str = timestamp.strftime("%H:%M:%S")
            action = record["action_type"]
            label = config.ACTION_LABELS.get(action, action)
            note = record["note"]
            
            note_str = f" ({note})" if note else ""
            
            record_list.append({
                "action_type": action,
                "time": time_str,
                "note": record["note"]
            })
            
            history_text += f"- {time_str} - {label}{note_str}\n"
        
        return {
            "success": True,
            "message": history_text,
            "records": record_list
        }
    
    @staticmethod
    def get_week_history(telegram_id: int) -> dict:
        """Lấy lịch sử chấm công tuần này"""
        db = get_db()
        
        user = user_service.UserService.get_user(telegram_id)
        if not user:
            return {
                "success": False,
                "message": "Ban chua dang ky!"
            }
        
        user_id = user["id"]
        
        # Lấy 7 ngày gần nhất
        today = date.today()
        week_ago = today - timedelta(days=6)
        
        summaries = db.fetchall(
            """
            SELECT date, check_in_time, check_out_time, total_work_minutes, break_minutes
            FROM daily_summaries
            WHERE user_id = ? AND date >= ? AND date <= ?
            ORDER BY date DESC
            """,
            (user_id, week_ago, today)
        )
        
        if not summaries:
            return {
                "success": True,
                "message": "Lich su cham cong tuan nay:\n\nChua co ban ghi nao!",
                "records": []
            }
        
        history_text = "Lich su cham cong tuan nay:\n\n"
        total_work = 0
        
        for row in summaries:
            date_str = row["date"]
            check_in = row["check_in_time"]
            check_out = row["check_out_time"]
            work_minutes = row["total_work_minutes"] or 0
            
            total_work += work_minutes
            
            check_in_str = "Nghi" if not check_in else dt.fromisoformat(check_in).strftime("%H:%M")
            check_out_str = "Nghi" if not check_out else dt.fromisoformat(check_out).strftime("%H:%M")
            hours = work_minutes // 60
            minutes = work_minutes % 60
            
            history_text += f"{date_str}: {check_in_str} - {check_out_str} ({hours}h {minutes}p)\n"
        
        total_hours = total_work // 60
        total_mins = total_work % 60
        history_text += f"\nTong thoi gian: {total_hours}h {total_mins}p"
        
        return {
            "success": True,
            "message": history_text,
            "records": summaries
        }
