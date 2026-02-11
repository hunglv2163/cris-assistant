# Hướng Dẫn Deploy Cris Assistant Lên Server

Để deploy bot này lên server (VPS Linux - Ubuntu/Debian/CentOS), bạn có 2 cách phổ biến: **Sử dụng Docker (Khuyên dùng)** hoặc **Chạy trực tiếp với Systemd**.

## Chuẩn bị trước
1.  **Thuê VPS**: Có thể dùng DigitalOcean, Vultr, AWS, hoặc Google Cloud. (Cấu hình thấp nhất 1CPU, 1GB RAM là đủ).
2.  **SSH vào server**: `ssh root@<ip-server>`
3.  **Cài đặt Git**: `sudo apt update && sudo apt install git -y`

---

## Cách 1: Sử dụng Docker (Nhanh gọn, ổn định)
Đây là cách dễ quản lý nhất, tự động khởi động lại khi server reboot hoặc bot bị lỗi.

### B1: Cài đặt Docker & Docker Compose
```bash
# Cài Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Kiểm tra
docker --version
docker compose version
```

### B2: Clone code về server
```bash
git clone https://github.com/hunglv2163/cris-assistant.git
cd cris-assistant
```

### B3: Tạo file cấu hình (.env)
Bạn cần tạo file `.env` chứa token của bot.
```bash
nano .env
```
Dán nội dung sau vào (thay thế bằng key thật của bạn):
```env
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
OPENAI_API_KEY=your_openai_api_key_here
MKT_CHAT_ID=-1003617346575
BD_CHAT_ID=-4875285470
```
Lưu lại: Nhấn `Ctrl+O` -> `Enter` -> `Ctrl+X`.

### B4: Tạo file database rỗng (để Docker mount được)
```bash
touch bot_data.db
```

### B5: Chạy Bot
```bash
docker compose up -d --build
```
Bot sẽ chạy ngầm. Để xem log:
```bash
docker compose logs -f
```

---

## Cách 2: Chạy trực tiếp (Python + Systemd)
Dùng cách này nếu bạn không muốn cài Docker.

### B1: Cài Python & Virtualenv
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv -y
```

### B2: Clone code & Setup
```bash
git clone https://github.com/hunglv2163/cris-assistant.git
cd cris-assistant

# Tạo môi trường ảo
python3 -m venv venv
source venv/bin/activate

# Cài thư viện
pip install -r requirements.txt

# Tạo .env như Bước 3 ở trên
nano .env
```

### B3: Chạy thử
```bash
python bot.py
```
Nếu chạy OK thì bấm `Ctrl+C` để tắt và cài đặt chạy nền bằng Systemd.

### B4: Tạo Service chạy nền
Tạo file service:
```bash
sudo nano /etc/systemd/system/cris-bot.service
```
Dán nội dung sau (sửa đường dẫn `/root/cris-assistant` nếu bạn clone vào chỗ khác):
```ini
[Unit]
Description=Cris Assistant Telegram Bot
After=network.target

[Service]
User=root
WorkingDirectory=/root/cris-assistant
ExecStart=/root/cris-assistant/venv/bin/python bot.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```
Lưu lại.

### B5: Kích hoạt Service
```bash
sudo systemctl daemon-reload
sudo systemctl enable cris-bot
sudo systemctl start cris-bot
```
Kiểm tra trạng thái:
```bash
sudo systemctl status cris-bot
```

---

## Cập nhật code mới
Khi bạn có thay đổi code và push lên GitHub, chỉ cần vào server và chạy:

**Nếu dùng Docker:**
```bash
cd cris-assistant
git pull
docker compose up -d --build
```

**Nếu dùng Systemd:**
```bash
cd cris-assistant
git pull
sudo systemctl restart cris-bot
```
