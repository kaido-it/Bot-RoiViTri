"""
Callback Handler - Xử lý các callback từ inline buttons
"""
from telegram import Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    ContextTypes
)

import config
from src.bot.services import attendance_service
from src.bot.handlers import keyboard


LOCATION_MAP = {
    "location_home": "Ve nha",
    "location_work": "Cong viec",
    "location_move": "Di chuyen",
    "location_other": "Khac"
}

LEAVE_TIME_MAP = {
    "leave_15": 15,
    "leave_30": 30,
    "leave_60": 60,
    "leave_120": 120,
    "leave_unlimited": None
}


async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Xử lý tất cả callbacks"""
    query = update.callback_query
    await query.answer()  # Trả lời callback để loading biến mất
    
    callback_data = query.data
    user = update.effective_user
    telegram_id = user.id
    
    # Parse callback data
    action, args = keyboard.parse_callback_data(callback_data)
    
    # Xử lý leave time (ra ca)
    if callback_data in LEAVE_TIME_MAP:
        minutes = LEAVE_TIME_MAP[callback_data]
        
        if callback_data == "leave_cancel":
            await query.edit_message_text(text="Da huy.")
            return
        
        result = attendance_service.AttendanceService.record_action(
            telegram_id=telegram_id,
            action_type=config.ACTION_BREAK_START,
            note=f"{minutes} phut" if minutes else "Khong gioi han"
        )
        
        if result["success"]:
            time_msg = f"{minutes} phut" if minutes else "khong gioi han"
            await query.edit_message_text(
                text=f"{result['message']}\n\nThoi gian nghi: {time_msg}"
            )
        else:
            await query.edit_message_text(text=result["message"])
        return
    
    # Xử lý location (rời vị trí)
    if callback_data in LOCATION_MAP:
        reason = LOCATION_MAP[callback_data]
        
        if callback_data == "location_cancel":
            await query.edit_message_text(text="Da huy.")
            return
        
        result = attendance_service.AttendanceService.record_action(
            telegram_id=telegram_id,
            action_type=config.ACTION_CHECK_OUT,
            note=reason
        )
        
        if result["success"]:
            await query.edit_message_text(text=result["message"])
        else:
            await query.edit_message_text(text=result["message"])
        return
    
    # Các callback cũ
    if action == keyboard.CallbackData.CHECK_IN:
        result = attendance_service.AttendanceService.record_action(
            telegram_id=telegram_id,
            action_type=config.ACTION_CHECK_IN
        )
        await query.edit_message_text(
            text=f"{result['message']}" if result["success"] else f"{result['message']}"
        )
    
    elif action == keyboard.CallbackData.BREAK_START:
        # Hiển thị keyboard chọn thời gian
        await query.edit_message_text(
            text="Ban muon nghi bao lau?",
            reply_markup=keyboard.get_confirm_leave_keyboard()
        )
    
    elif action == keyboard.CallbackData.CHECK_OUT:
        # Hiển thị keyboard chọn lý do
        await query.edit_message_text(
            text="Ban muon roi vi tri de lam gi?",
            reply_markup=keyboard.get_location_keyboard()
        )
    
    elif action == keyboard.CallbackData.BACK_TO_WORK:
        result = attendance_service.AttendanceService.record_action(
            telegram_id=telegram_id,
            action_type=config.ACTION_BREAK_END
        )
        if result["success"]:
            await query.edit_message_text(
                text=result["message"],
                reply_markup=keyboard.get_main_keyboard()
            )
        else:
            await query.edit_message_text(text=result["message"])
    
    elif action == keyboard.CallbackData.HISTORY:
        result = attendance_service.AttendanceService.get_today_history(telegram_id)
        await query.edit_message_text(text=result["message"])
    
    elif action == keyboard.CallbackData.WEEK:
        result = attendance_service.AttendanceService.get_week_history(telegram_id)
        await query.edit_message_text(text=result["message"])
    
    elif action == keyboard.CallbackData.BACK_TO_MENU:
        await query.edit_message_text(
            text="Menu chinh\n\nChon chuc nang:",
            reply_markup=keyboard.get_main_inline_keyboard()
        )
    
    elif action == keyboard.CallbackData.HELP:
        await query.edit_message_text(text=config.HELP_MESSAGE)
    
    else:
        await query.edit_message_text(text="Action khong hop le")


def register_callback_handlers(application: Application):
    """Đăng ký callback handlers"""
    application.add_handler(CallbackQueryHandler(callback_handler))
