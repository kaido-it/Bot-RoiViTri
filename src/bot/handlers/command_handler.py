"""
Command Handler - Xử lý các commands từ người dùng
"""
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler
)

import config
from src.bot.services import user_service, attendance_service
from src.bot.handlers import keyboard


# Conversation states
(AWAITING_FULL_NAME, AWAITING_LEAVE_REASON, AWAITING_LEAVE_TIME) = range(1, 4)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Xử lý command /start"""
    user = update.effective_user
    telegram_id = user.id
    username = user.username
    first_name = user.first_name
    last_name = user.last_name
    
    full_name = f"{first_name} {last_name}".strip() if last_name else first_name
    
    # Kiểm tra user đã đăng ký chưa
    if user_service.UserService.is_registered(telegram_id):
        await update.message.reply_text(
            text=f"Xin chao {full_name}! 👋\n\nBot da san sang. Su dung menu ben duoi de cham cong:",
            reply_markup=keyboard.get_main_keyboard()
        )
    else:
        # Tạo user mới
        user_service.UserService.create_user(
            telegram_id=telegram_id,
            username=username,
            full_name=full_name
        )
        
        await update.message.reply_text(
            text=f"Dang ky thanh cong!\n\n"
                 f"Chao muc {full_name}!\n\n"
                 f"Ban co the su dung cac chuc nang ben duoi:",
            reply_markup=keyboard.get_main_keyboard()
        )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Xử lý command /help"""
    await update.message.reply_text(
        text=config.HELP_MESSAGE,
        parse_mode="Markdown",
        reply_markup=keyboard.get_main_keyboard()
    )


async def menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Xử lý command /menu - hiển thị menu chính"""
    await update.message.reply_text(
        text="Menu chinh\n\nChon chuc nang:",
        parse_mode="Markdown",
        reply_markup=keyboard.get_main_keyboard()
    )


async def check_in_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Xử lý báo lên ca"""
    user = update.effective_user
    telegram_id = user.id
    
    result = attendance_service.AttendanceService.record_action(
        telegram_id=telegram_id,
        action_type=config.ACTION_CHECK_IN
    )
    
    if result["success"]:
        await update.message.reply_text(
            text=f"{result['message']}",
            parse_mode="Markdown"
        )
    else:
        await update.message.reply_text(
            text=f"{result['message']}",
            parse_mode="Markdown"
        )


async def break_start_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Xử lý ra ca - hỏi thời gian nghỉ"""
    user = update.effective_user
    telegram_id = user.id
    
    # Hiển keyboard chọn thời gian nghỉ
    await update.message.reply_text(
        text="Ban muon nghi bao lau?",
        reply_markup=keyboard.get_confirm_leave_keyboard()
    )


async def break_start_with_time(update: Update, context: ContextTypes.DEFAULT_TYPE, minutes: int = None):
    """Xử lý ra ca với thời gian cụ thể"""
    user = update.effective_user
    telegram_id = user.id
    
    result = attendance_service.AttendanceService.record_action(
        telegram_id=telegram_id,
        action_type=config.ACTION_BREAK_START,
        note=f"{minutes} phut" if minutes else "Khong gioi han"
    )
    
    if result["success"]:
        # Hiển thị keyboard với nút quay lại làm việc
        time_msg = f"{minutes} phut" if minutes else "khong gioi han"
        await update.message.reply_text(
            text=f"{result['message']}\n\nThoi gian nghi: {time_msg}",
            reply_markup=keyboard.get_break_keyboard()
        )
    else:
        await update.message.reply_text(
            text=f"{result['message']}",
            parse_mode="Markdown"
        )


async def back_to_work_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Xử lý quay lại làm việc sau khi nghỉ"""
    user = update.effective_user
    telegram_id = user.id
    
    result = attendance_service.AttendanceService.record_action(
        telegram_id=telegram_id,
        action_type=config.ACTION_BREAK_END
    )
    
    if result["success"]:
        await update.message.reply_text(
            text=f"{result['message']}",
            reply_markup=keyboard.get_main_keyboard()
        )
    else:
        await update.message.reply_text(
            text=f"{result['message']}",
            parse_mode="Markdown"
        )


async def break_end_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Xử lý vào ca (sau khi nghỉ)"""
    user = update.effective_user
    telegram_id = user.id
    
    result = attendance_service.AttendanceService.record_action(
        telegram_id=telegram_id,
        action_type=config.ACTION_BREAK_END
    )
    
    if result["success"]:
        await update.message.reply_text(
            text=f"{result['message']}",
            parse_mode="Markdown"
        )
    else:
        await update.message.reply_text(
            text=f"{result['message']}",
            parse_mode="Markdown"
        )


async def check_out_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Xử lý rời vị trí - hiển thị keyboard chọn lý do"""
    user = update.effective_user
    telegram_id = user.id
    
    # Kiểm tra đã check-in hôm nay chưa
    if not attendance_service.AttendanceService.has_checked_in_today(telegram_id):
        await update.message.reply_text(
            text="Ban chua bao len ca hom nay!",
            parse_mode="Markdown"
        )
        return
    
    # Hiển thị keyboard chọn lý do rời vị trí
    await update.message.reply_text(
        text="Ban muon roi vi tri de lam gi?",
        reply_markup=keyboard.get_location_keyboard()
    )


async def check_out_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE, reason: str = None):
    """Xử lý rời vị trí với lý do"""
    user = update.effective_user
    telegram_id = user.id
    
    result = attendance_service.AttendanceService.record_action(
        telegram_id=telegram_id,
        action_type=config.ACTION_CHECK_OUT,
        note=reason
    )
    
    if result["success"]:
        await update.message.reply_text(
            text=f"{result['message']}",
            parse_mode="Markdown"
        )
    else:
        await update.message.reply_text(
            text=f"{result['message']}",
            parse_mode="Markdown"
        )


async def history_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Xử lý xem lịch sử"""
    user = update.effective_user
    telegram_id = user.id
    
    result = attendance_service.AttendanceService.get_today_history(telegram_id)
    
    await update.message.reply_text(
        text=result["message"],
        parse_mode="Markdown"
    )


async def week_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Xử lý xem lịch sử tuần"""
    user = update.effective_user
    telegram_id = user.id
    
    result = attendance_service.AttendanceService.get_week_history(telegram_id)
    
    await update.message.reply_text(
        text=result["message"],
        parse_mode="Markdown"
    )


async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Xử lý text message từ keyboard"""
    text = update.message.text
    
    if text == "🚀 Báo lên ca":
        await check_in_action(update, context)
    elif text == "☕ Ra ca":
        await break_start_action(update, context)
    elif text == "👋 Rời vị trí":
        await check_out_action(update, context)
    elif text == "✅ Quay lại làm việc":
        await back_to_work_action(update, context)
    elif text == "📋 Lịch sử":
        await history_action(update, context)
    elif text == "📊 Tuần này":
        await week_action(update, context)
    elif text == "❓ Trợ giúp" or text == "/help":
        await help_command(update, context)
    else:
        await update.message.reply_text(
            text="Toi khong hieu. Vui long su dung menu ben duoi:",
            reply_markup=keyboard.get_main_keyboard()
        )


def register_handlers(application: Application):
    """Đăng ký tất cả handlers"""
    
    # Command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("menu", menu_command))
    
    # Message handler - xử lý text từ keyboard
    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle_text_message
        )
    )
