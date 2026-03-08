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


async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Xử lý tất cả callbacks"""
    query = update.callback_query
    await query.answer()  # Trả lời callback để loading biến mất
    
    callback_data = query.data
    user = update.effective_user
    telegram_id = user.id
    
    # Parse callback data
    action, args = keyboard.parse_callback_data(callback_data)
    
    if action == keyboard.CallbackData.CHECK_IN:
        result = attendance_service.AttendanceService.record_action(
            telegram_id=telegram_id,
            action_type=config.ACTION_CHECK_IN
        )
        await query.edit_message_text(
            text=f"✅ *{result['message']}*" if result["success"] else f"⚠️ *{result['message']}*",
            parse_mode="Markdown"
        )
    
    elif action == keyboard.CallbackData.BREAK_START:
        result = attendance_service.AttendanceService.record_action(
            telegram_id=telegram_id,
            action_type=config.ACTION_BREAK_START
        )
        await query.edit_message_text(
            text=f"☕ *{result['message']}*" if result["success"] else f"⚠️ *{result['message']}*",
            parse_mode="Markdown"
        )
    
    elif action == keyboard.CallbackData.CHECK_OUT:
        result = attendance_service.AttendanceService.record_action(
            telegram_id=telegram_id,
            action_type=config.ACTION_CHECK_OUT
        )
        await query.edit_message_text(
            text=f"👋 *{result['message']}*" if result["success"] else f"⚠️ *{result['message']}*",
            parse_mode="Markdown"
        )
    
    elif action == keyboard.CallbackData.HISTORY:
        result = attendance_service.AttendanceService.get_today_history(telegram_id)
        await query.edit_message_text(
            text=result["message"],
            parse_mode="Markdown"
        )
    
    elif action == keyboard.CallbackData.WEEK:
        result = attendance_service.AttendanceService.get_week_history(telegram_id)
        await query.edit_message_text(
            text=result["message"],
            parse_mode="Markdown"
        )
    
    elif action == keyboard.CallbackData.BACK_TO_MENU:
        await query.edit_message_text(
            text="📋 *Menu chính*\n\nChọn chức năng:",
            parse_mode="Markdown",
            reply_markup=keyboard.get_main_inline_keyboard()
        )
    
    elif action == keyboard.CallbackData.HELP:
        await query.edit_message_text(
            text=config.HELP_MESSAGE,
            parse_mode="Markdown"
        )
    
    else:
        await query.edit_message_text(
            text="❓ Action không hợp lệ",
            parse_mode="Markdown"
        )


def register_callback_handlers(application: Application):
    """Đăng ký callback handlers"""
    application.add_handler(CallbackQueryHandler(callback_handler))
