"""
Bot Telegram Chấm Công - Rời Vị Trí
Entry point của ứng dụng
"""
import os
import sys
from telegram.ext import Application

# Thêm thư mục gốc vào sys.path để import được config
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
from src.bot.handlers import command_handler, callback_handler


def main():
    """Hàm chính để chạy bot"""
    
    # Kiểm tra BOT_TOKEN
    if config.BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("❌ LỖI: Bạn cần cập nhật BOT_TOKEN trong file config.py!")
        print("\n📝 Hướng dẫn lấy BOT_TOKEN:")
        print("1. Mở Telegram và tìm @BotFather")
        print("2. Gửi /newbot để tạo bot mới")
        print("3. Làm theo hướng dẫn để đặt tên bot")
        print("4. BotFather sẽ cấp cho bạn một token")
        print("5. Cập nhật BOT_TOKEN trong file config.py")
        return
    
    print("🤖 Bot Telegram Chấm Công đang khởi động...")
    print(f"📂 Database: {config.DATABASE_CONFIG['path']}")
    
    # Tạo Application
    application = Application.builder().token(config.BOT_TOKEN).build()
    
    # Đăng ký handlers
    command_handler.register_handlers(application)
    callback_handler.register_callback_handlers(application)
    
    print("✅ Đăng ký handlers thành công!")
    print("\n🚀 Bot đang chạy...")
    print("Nhấn Ctrl+C để dừng bot\n")
    
    # Chạy bot (polling)
    application.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
