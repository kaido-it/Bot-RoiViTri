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
                "message": "Bạn chưa đăng ký! Vui lòng dùng /start để đăng ký."
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
                    "message": "Bạn đã báo lên ca hôm nay rồi!"
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
                    "message": "Bạn chưa báo lên ca hôm nay!"
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
                    "message": "Bạn đã rời vị trí hôm nay rồi!"
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
        message = AttendanceService._get_action_message(action_type, time_str)
        
        # Nếu là checkout, tính tổng thời gian làm việc
        if action_type == config.ACTION_CHECK_OUT:
            work_minutes = AttendanceService._get_today_work_minutes(user_id)
            hours = work_minutes // 60
            minutes = work_minutes % 60
            message += f"\n📊 Tổng thời gian làm việc: {hours}h {minutes}p"
        
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
    def _get_action_message(action_type: str, time_str: str) -> str:
        """Tạo thông báo cho từng action"""
        messages = {
            config.ACTION_CHECK_IN: f"✅ Bạn đã báo lên ca lúc {time_str}\nThời gian làm việc bắt đầu được ghi nhận!",
            config.ACTION_BREAK_START: f"☕ Bạn đã ra ca lúc {time_str}\nThời gian nghỉ được ghi nhận!",
            config.ACTION_BREAK_END: f"✅ Bạn đã vào ca lúc {time_str}\nTiếp tục làm việc nhé!",
            config.ACTION_CHECK_OUT: f"👋 Bạn đã rời vị trí lúc {time_str}\nHẹn gặp lại!"
        }
        return messages.get(action_type, "Hành động được ghi nhận!")
    
    @staticmethod
    def get_today_history(telegram_id: int) -> dict:
        """Lấy lịch sử chấm công hôm nay"""
        db = get_db()
        
        user = user_service.UserService.get_user(telegram_id)
        if not user:
            return {
                "success": False,
                "message": "Bạn chưa đăng ký!"
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
                "message": "📋 Lịch sử chấm công hôm nay:\n\nChưa có bản ghi nào!",
                "records": []
            }
        
        # Tạo danh sách records
        record_list = []
        history_text = "📋 *Lịch sử chấm công hôm nay:*\n\n"
        
        for record in records:
            timestamp = dt.fromisoformat(record["timestamp"])
            time_str = timestamp.strftime("%H:%M:%S")
            action = record["action_type"]
            label = config.ACTION_LABELS.get(action, action)
            
            record_list.append({
                "action_type": action,
                "time": time_str,
                "note": record["note"]
            })
            
            history_text += f"• {time_str} - {label}\n"
        
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
                "message": "Bạn chưa đăng ký!"
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
                "message": "📊 Lịch sử chấm công tuần này:\n\nChưa có bản ghi nào!",
                "records": []
            }
        
        history_text = "📊 *Lịch sử chấm công tuần này:*\n\n"
        total_work = 0
        
        for row in summaries:
            date_str = row["date"]
            check_in = row["check_in_time"]
            check_out = row["check_out_time"]
            work_minutes = row["total_work_minutes"] or 0
            
            total_work += work_minutes
            
            check_in_str = "Nghỉ" if not check_in else dt.fromisoformat(check_in).strftime("%H:%M")
            check_out_str = "Nghỉ" if not check_out else dt.fromisoformat(check_out).strftime("%H:%M")
            hours = work_minutes // 60
            minutes = work_minutes % 60
            
            history_text += f"📅 {date_str}: {check_in_str} - {check_out_str} ({hours}h{minutes}p)\n"
        
        total_hours = total_work // 60
        total_mins = total_work % 60
        history_text += f"\n📈 Tổng thời gian: {total_hours}h {total_mins}p"
        
        return {
            "success": True,
            "message": history_text,
            "records": summaries
        }
