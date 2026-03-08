"""
Keyboard - Tạo các nút bấm cho Bot
"""
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ConversationHandler

import config


def get_main_keyboard() -> ReplyKeyboardMarkup:
    """
    Tạo keyboard chính với các nút chức năng
    Sử dụng ReplyKeyboardMarkup cho keyboard cố định
    """
    keyboard = [
        [KeyboardButton(text="🚀 Báo lên ca"), KeyboardButton(text="☕ Ra ca")],
        [KeyboardButton(text="👋 Rời vị trí"), KeyboardButton(text="📋 Lịch sử")],
        [KeyboardButton(text="📊 Tuần này"), KeyboardButton(text="❓ Trợ giúp")]
    ]
    
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        one_time_keyboard=False
    )


def get_main_inline_keyboard() -> InlineKeyboardMarkup:
    """
    Tạo inline keyboard chính
    Sử dụng InlineKeyboardMarkup cho inline buttons
    """
    keyboard = [
        [
            InlineKeyboardButton(text="🚀 Báo lên ca", callback_data="action_check_in"),
            InlineKeyboardButton(text="☕ Ra ca", callback_data="action_break_start")
        ],
        [
            InlineKeyboardButton(text="👋 Rời vị trí", callback_data="action_check_out"),
            InlineKeyboardButton(text="📋 Lịch sử", callback_data="action_history")
        ],
        [
            InlineKeyboardButton(text="📊 Tuần này", callback_data="action_week")
        ]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_action_keyboard() -> InlineKeyboardMarkup:
    """
    Keyboard cho các action (báo ca, ra ca, về)
    """
    keyboard = [
        [
            InlineKeyboardButton(text="✅ Xác nhận", callback_data="confirm_yes"),
            InlineKeyboardButton(text="❌ Hủy", callback_data="confirm_no")
        ]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_registration_keyboard() -> InlineKeyboardMarkup:
    """
    Keyboard cho đăng ký
    """
    keyboard = [
        [
            InlineKeyboardButton(text="✅ Đăng ký ngay", callback_data="register_start")
        ]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


# Callback data constants
class CallbackData:
    # Action callbacks
    CHECK_IN = "action_check_in"
    BREAK_START = "action_break_start"
    BREAK_END = "action_break_end"
    CHECK_OUT = "action_check_out"
    HISTORY = "action_history"
    WEEK = "action_week"
    
    # Confirmation callbacks
    CONFIRM_YES = "confirm_yes"
    CONFIRM_NO = "confirm_no"
    
    # Registration callbacks
    REGISTER_START = "register_start"
    REGISTER_SUBMIT = "register_submit"
    
    # Navigation callbacks
    BACK_TO_MENU = "back_to_menu"
    HELP = "help"


def create_callback_data(action: str, *args) -> str:
    """Tạo callback data với tham số"""
    if args:
        return f"{action}:{':'.join(str(arg) for arg in args)}"
    return action


def parse_callback_data(callback_data: str) -> tuple:
    """Parse callback data thành tuple (action, args)"""
    parts = callback_data.split(":", 1)
    action = parts[0]
    args = parts[1].split(":") if len(parts) > 1 else []
    return (action, args)
