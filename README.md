# 🤖 Bot Telegram Chấm Công - Rời Vị Trí

Bot Telegram giúp quản lý chấm công, theo dõi thời gian làm việc của nhân viên với các chức năng: báo lên ca, ra ca, rời vị trí và xem lịch sử chấm công.

## 📋 Tính năng

| Tính năng | Mô tả |
|-----------|-------|
| 🚀 **Báo lên ca** | Check-in đầu ca làm việc |
| ☕ **Ra ca** | Nghỉ giải lao/bắt đầu nghỉ |
| 👋 **Rời vị trí** | Check-out kết thúc ca làm việc |
| 📋 **Xem lịch sử** | Xem bản ghi chấm công hôm nay |
| 📊 **Tuần này** | Xem lịch sử chấm công 7 ngày gần nhất |

## 🛠️ Công nghệ

- **Ngôn ngữ:** Python 3.x
- **Thư viện Bot:** python-telegram-bot 20.8
- **Database:** SQLite (nhẹ, không cần cài đặt)

## 📁 Cấu trúc dự án

```
Bot-RoiViTri/
├── config.py                 # Cấu hình bot
├── requirements.txt         # Thư viện cần thiết
├── README.md                # File hướng dẫn này
└── src/
    ├── main.py              # Entry point của bot
    └── bot/
        ├── database/
        │   └── db.py        # Kết nối SQLite
        ├── services/
        │   ├── user_service.py          # Quản lý người dùng
        │   └── attendance_service.py    # Logic chấm công
        └── handlers/
            ├── keyboard.py              # Tạo keyboard
            ├── command_handler.py        # Xử lý commands
            └── callback_handler.py      # Xử lý callbacks
```

## 🚀 Cách cài đặt và chạy

### Bước 1: Clone hoặc tải dự án

```bash
git clone <repository-url>
cd Bot-RoiViTri
```

### Bước 2: Cài đặt thư viện

```bash
pip install -r requirements.txt
```

### Bước 3: Lấy Bot Token

1. Mở Telegram và tìm kiếm **@BotFather**
2. Gửi lệnh `/newbot` để tạo bot mới
3. Làm theo hướng dẫn để đặt tên cho bot (ví dụ: `Bot Chấm Công`)
4. Sau khi hoàn tất, BotFather sẽ cấp cho bạn một **Token** (dạng: `123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11`)
5. **Copy token này**

### Bước 4: Cấu hình Bot Token

Mở file [`config.py`](config.py) và thay thế:

```python
# Đổi từ:
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")

# Thành:
BOT_TOKEN = "YOUR_ACTUAL_TOKEN_HERE"
```

Hoặc sử dụng biến môi trường:

```bash
# Linux/Mac:
export BOT_TOKEN="your_token_here"

# Windows (cmd):
set BOT_TOKEN=your_token_here
```

### Bước 5: Chạy bot

```bash
python src/main.py
```

Nếu thành công, bạn sẽ thấy:

```
🤖 Bot Telegram Chấm Công đang khởi động...
📂 Database: C:\Users\...\data\attendance.db
✅ Đăng ký handlers thành công!

🚀 Bot đang chạy...
Nhấn Ctrl+C để dừng bot
```

## 📱 Cách sử dụng Bot

### 1. Đăng ký

- Mở Telegram và tìm bot của bạn (theo tên bạn đặt ở bước 3)
- Gửi lệnh `/start` để bắt đầu
- Bot sẽ tự động đăng ký tài khoản của bạn

### 2. Sử dụng các chức năng

Gửi tin nhắn hoặc nhấn vào các nút:

| Nút | Chức năng |
|------|-----------|
| 🚀 Báo lên ca | Bắt đầu ca làm việc |
| ☕ Ra ca | Bắt đầu nghỉ giải lao |
| 👋 Rời vị trí | Kết thúc ca làm việc |
| 📋 Lịch sử | Xem chấm công hôm nay |
| 📊 Tuần này | Xem 7 ngày gần nhất |

### 3. Commands

| Command | Mô tả |
|---------|-------|
| `/start` | Bắt đầu / Đăng ký |
| `/menu` | Hiển thị menu chính |
| `/help` | Xem hướng dẫn |

## 💾 Dữ liệu

Dữ liệu được lưu trong file SQLite: `data/attendance.db`

### Các bảng trong Database:

1. **users** - Thông tin người dùng
2. **attendance_records** - Bản ghi chấm công
3. **daily_summaries** - Tổng hợp hàng ngày

## 🔒 Lưu ý bảo mật

- **Token Bot:** Không chia sẻ token cho người khác
- **Database:** File `attendance.db` chứa dữ liệu cá nhân, cần bảo mật
- **Server:** Nên chạy bot trên server/VPS để hoạt động 24/7

## 🖥️ Chạy bot 24/7 trên Server

### Sử dụng PM2 (Linux):

```bash
# Cài đặt PM2
npm install -g pm2

# Chạy bot
pm2 start src/main.py --name bot-cham-cong

# Xem log
pm2 logs bot-cham-cong

# Tự động khởi động lại khi server restart
pm2 startup
pm2 save
```

### Sử dụng systemd (Linux):

Tạo file `/etc/systemd/system/bot-cham-cong.service`:

```ini
[Unit]
Description=Bot Telegram Chấm Công
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/Bot-RoiViTri
ExecStart=/usr/bin/python3 src/main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Kích hoạt:

```bash
sudo systemctl daemon-reload
sudo systemctl enable bot-cham-cong
sudo systemctl start bot-cham-cong
```

## 🐛 Xử lý lỗi thường gặp

| Lỗi | Nguyên nhân | Cách khắc phục |
|-----|-------------|----------------|
| `Invalid token` | Token không đúng | Kiểm tra lại token trong config.py |
| `Connection error` | Mất kết nối internet | Kiểm tra kết nối mạng |
| `Database locked` | Nhiều process truy cập DB | Khởi động lại bot |

## 📝 Giấy phép

MIT License - Tự do sử dụng và phát triển

---

Made with ❤️ for Vietnamese users
