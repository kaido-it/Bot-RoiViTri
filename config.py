"""
Cấu hình cho Bot Telegram Chấm Công
"""
import os
from pathlib import Path

# Đường dẫn thư mục gốc của dự án
BASE_DIR = Path(__file__).resolve().parent

# Đường dẫn database SQLite
DATABASE_PATH = BASE_DIR / "data" / "attendance.db"

# Telegram Bot Token - LẤY TỪ @BotFather
BOT_TOKEN = os.getenv("BOT_TOKEN", "8113902916:AAHvqM6siiVHAkdmH26KNjuXxI9Rh1i0mjE")

# Cấu hình Database
DATABASE_CONFIG = {
    "path": str(DATABASE_PATH)
}

# Tin nhắn chào mừng
WELCOME_MESSAGE = """
🤖 *Chào mừng bạn đến với Bot Chấm Công!*

Bot này giúp bạn quản lý thời gian làm việc dễ dàng.

📋 *Các chức năng:*
• 🚀 Báo lên ca - Bắt đầu làm việc
• ☕ Ra ca - Nghỉ giải lao
• 👋 Rời vị trí - Kết thúc làm việc
• 📋 Xem lịch sử - Xem bản ghi chấm công

⚠️ *Lưu ý:* Bạn cần đăng ký trước khi sử dụng!
"""

# Tin nhắn hướng dẫn
HELP_MESSAGE = """
📖 *Hướng dẫn sử dụng:*

/start - Bắt đầu / Đăng ký
/help - Xem hướng dẫn
/menu - Hiển thị menu chính

Nhấn các nút bên dưới để sử dụng các chức năng!
"""

# Các action types
ACTION_CHECK_IN = "check_in"
ACTION_BREAK_START = "break_start"
ACTION_BREAK_END = "break_end"
ACTION_CHECK_OUT = "check_out"

# Mapping action types để hiển thị
ACTION_LABELS = {
    ACTION_CHECK_IN: "Bao len ca",
    ACTION_BREAK_START: "Ra ca",
    ACTION_BREAK_END: "Quay lai lam viec",
    ACTION_CHECK_OUT: "Roi vi tri"
}
