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


def get_break_keyboard() -> ReplyKeyboardMarkup:
    """
    Keyboard khi đang trong giờ nghỉ - có nút quay lại làm việc
    """
    keyboard = [
        [KeyboardButton(text="✅ Quay lại làm việc")],
        [KeyboardButton(text="📋 Lịch sử"), KeyboardButton(text="❓ Trợ giúp")]
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


def get_location_keyboard() -> InlineKeyboardMarkup:
    """
    Keyboard để chọn lý do rời vị trí
    """
    keyboard = [
        [
            InlineKeyboardButton(text="🏠 Về nhà", callback_data="location_home"),
            InlineKeyboardButton(text="🏢 Công việc", callback_data="location_work")
        ],
        [
            InlineKeyboardButton(text="🚗 Di chuyển", callback_data="location_move"),
            InlineKeyboardButton(text="📝 Khác", callback_data="location_other")
        ],
        [
            InlineKeyboardButton(text="❌ Hủy", callback_data="location_cancel")
        ]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_confirm_leave_keyboard() -> InlineKeyboardMarkup:
    """
    Keyboard xác nhận rời vị trí với thời gian
    """
    keyboard = [
        [
            InlineKeyboardButton(text="15 phút", callback_data="leave_15"),
            InlineKeyboardButton(text="30 phút", callback_data="leave_30"),
            InlineKeyboardButton(text="60 phút", callback_data="leave_60")
        ],
        [
            InlineKeyboardButton(text="120 phút", callback_data="leave_120"),
            InlineKeyboardButton(text="Không giới hạn", callback_data="leave_unlimited")
        ],
        [
            InlineKeyboardButton(text="❌ Hủy", callback_data="leave_cancel")
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
    BACK_TO_WORK = "action_back_to_work"
    HISTORY = "action_history"
    WEEK = "action_week"
    
    # Location callbacks
    LOCATION_HOME = "location_home"
    LOCATION_WORK = "location_work"
    LOCATION_MOVE = "location_move"
    LOCATION_OTHER = "location_other"
    LOCATION_CANCEL = "location_cancel"
    
    # Leave time callbacks
    LEAVE_15 = "leave_15"
    LEAVE_30 = "leave_30"
    LEAVE_60 = "leave_60"
    LEAVE_120 = "leave_120"
    LEAVE_UNLIMITED = "leave_unlimited"
    LEAVE_CANCEL = "leave_cancel"
    
    # Confirmation callbacks
    CONFIRM_YES = "confirm_yes"
    CONFIRM_NO = "confirm_no"
    
    # Registration callbacks
    REGISTER_START = "register_start"
    REGISTER_SUBMIT = "register_submit"
    
    # Navigation callbacks
    BACK_TO_MENU = "back_to_menu"
    HELP = "help"


# Leave time options (in minutes)
LEAVE_TIME_OPTIONS = {
    "15": 15,
    "30": 30,
    "60": 60,
    "120": 120,
    "unlimited": None
}


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
