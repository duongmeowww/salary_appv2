# HƯỚNG DẪN TRIỂN KHAI ỨNG DỤNG SALARY TRÊN PYTHONANYWHERE

## Bước 1: Tạo Tài Khoản PythonAnywhere
1. Truy cập https://www.pythonanywhere.com
2. Đăng ký tài khoản Free hoặc Paid
3. Xác nhận email

## Bước 2: Upload Code lên PythonAnywhere
### Cách 1: Sử dụng Web Interface
1. Đăng nhập vào PythonAnywhere
2. Mở "Files" tab
3. Tạo folder: salary_app
4. Upload tất cả file từ máy tính:
   - run.py
   - wsgi.py
   - requirements.txt
   - app/ folder (toàn bộ)
   - instance/ folder

### Cách 2: Sử dụng Git (Nên dùng)
1. Tạo repository Git trên GitHub
2. Push code lên GitHub
3. SSH vào PythonAnywhere:
   ```
   cd ~
   git clone https://github.com/YOUR_USERNAME/salary_app.git
   ```

## Bước 3: Tạo Virtual Environment
1. Mở "Consoles" tab trong PythonAnywhere
2. Tạo console mới "Bash"
3. Chạy các lệnh:
   ```bash
   cd ~/salary_app
   python3 -m venv venv
   source venv/bin/activate
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

## Bước 4: Cấu Hình Web App
1. Mở "Web" tab trong PythonAnywhere
2. Nhấn "+ Add a new web app"
3. Chọn "Manual configuration"
4. Chọn Python 3.10 (hoặc phiên bản mới hơn)
5. Cấu hình WSGI file:
   - Mở WSGI file config
   - Xóa nội dung mặc định
   - Paste nội dung file wsgi.py từ máy tính (không cần sửa đường dẫn, file tự xác định)
   - Lưu file
   - QUAN TRỌNG: tạo file `.env` trong thư mục project với `FLASK_ENV=production` và `SECRET_KEY=...`

## Bước 5: Cấu Hình Virtual Environment trong Web App
1. Trong "Web" tab, tìm mục "Virtualenv"
2. Nhập đường dẫn: /home/YOUR_USERNAME/salary_app/venv
3. Lưu lại

## Bước 6: Cấu Hình Static Files
1. Trong "Web" tab, tìm mục "Static files"
2. Thêm mapping:
   - URL: /static/
   - Directory: /home/YOUR_USERNAME/salary_app/app/static

## Bước 7: Tạo Database và Tài Khoản Admin
Trong Bash console:
```bash
cd ~/salary_app
source venv/bin/activate
export FLASK_APP=run.py
flask init-db
```
Lệnh này in ra mật khẩu admin được sinh ngẫu nhiên (hoặc dùng `--admin-password`).

## Bước 8: Khởi Động Web App
1. Click nút "Reload" (bên phải tên domain)
2. Chờ vài giây để app khởi động

## Bước 9: Truy Cập Ứng Dụng
- URL mặc định: https://YOUR_USERNAME.pythonanywhere.com
- Username: admin
- Password: mật khẩu do `flask init-db` sinh ra

## Troubleshooting

### Lỗi: ModuleNotFoundError
- Kiểm tra xem virtual environment đã được cấu hình đúng chưa
- Chạy lại: pip install -r requirements.txt

### Database không tạo được
1. SSH vào console
2. Chạy:
   ```bash
   cd ~/salary_app
   source venv/bin/activate
   export FLASK_APP=run.py
   flask init-db
   ```

### Lỗi Permission Denied
- Chạy: chmod 755 ~/salary_app -R

### Static files không load
- Kiểm tra đường dẫn trong cấu hình Static files
- Reload web app lại

## Các Bước Cập Nhật Code Sau Này
1. SSH vào console:
   ```bash
   cd ~/salary_app
   git pull  # nếu dùng Git
   # hoặc upload file mới nếu dùng web interface
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. Reload web app trong "Web" tab

## Thay Đổi SECRET_KEY (Bảo Mật)
Ứng dụng ở chế độ production sẽ từ chối khởi động nếu chưa đặt SECRET_KEY:
- Tạo khoá: `python -c "import secrets; print(secrets.token_hex(32))"`
- Thêm vào file `.env`: `SECRET_KEY=<giá trị vừa tạo>`
- Reload web app

## Backup Database
1. SSH vào console
2. Chạy: tar -czf database_backup.tar.gz instance/
3. Download file backup từ "Files" tab

## Tham Khảo
- PythonAnywhere Help: https://help.pythonanywhere.com
- Flask Docs: https://flask.palletsprojects.com
- SQLAlchemy Docs: https://docs.sqlalchemy.org
