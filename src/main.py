"""
Bot Telegram Chấm Công - Rời Vị Trí
Entry point của ứng dụng
"""
import os
import sys
from telegram.ext import Application

# Set UTF-8 encoding
os.environ['PYTHONIOENCODING'] = 'utf-8'
sys.stdout.reconfigure(encoding='utf-8')

# Thêm thư mục gốc vào sys.path để import được config
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
from src.bot.handlers import command_handler, callback_handler


def main():
    """Hàm chính để chạy bot"""
    
    # Kiểm tra BOT_TOKEN
    if config.BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("LOI: Ban can cap nhat BOT_TOKEN trong file config.py!")
        print("\nHuong dan lay BOT_TOKEN:")
        print("1. Mo Telegram va tim @BotFather")
        print("2. Gui /newbot de tao bot moi")
        print("3. Lam theo huong dan de dat ten bot")
        print("4. BotFather se cap cho ban mot token")
        print("5. Cap nhat BOT_TOKEN trong file config.py")
        return
    
    print("Bot Telegram Cham Cong dang khoi dong...")
    print(f"Database: {config.DATABASE_CONFIG['path']}")
    
    # Tạo Application
    application = Application.builder().token(config.BOT_TOKEN).build()
    
    # Đăng ký handlers
    command_handler.register_handlers(application)
    callback_handler.register_callback_handlers(application)
    
    print("Dang ky handlers thanh cong!")
    print("\nBot dang chay...")
    print("Nhan Ctrl+C de dung bot\n")
    
    # Chạy bot (polling)
    application.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
