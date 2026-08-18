# QUICK START - TẠO LIÊN KẾT GIT VÀ TRIỂN KHAI

## Nếu chưa có Git Repository

### Bước 1: Tạo Repository trên GitHub
1. Đăng nhập vào GitHub
2. Tạo repository mới (ví dụ: "salary_app")
3. Copy HTTPS URL

### Bước 2: Push Code lên GitHub
```bash
cd salary_app
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/salary_app.git
git push -u origin main
```

## Triển Khai Nhanh trên PythonAnywhere

### Bước 1: SSH vào PythonAnywhere
1. Đăng nhập vào https://www.pythonanywhere.com
2. Mở "Consoles" tab
3. Tạo console "Bash" mới
4. Chạy lệnh sau:

```bash
# Clone repository
cd ~
git clone https://github.com/YOUR_USERNAME/salary_app.git
cd salary_app

# Tạo virtual environment
python3 -m venv venv
source venv/bin/activate

# Cài đặt dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Khởi tạo database và tài khoản admin (in ra mật khẩu được sinh ngẫu nhiên)
export FLASK_APP=run.py
flask init-db
```

### Bước 2: Tạo Web App trong PythonAnywhere
1. Mở "Web" tab
2. Nhấn "+ Add a new web app"
3. Chọn "Manual configuration"
4. Chọn Python 3.10+ (hoặc newer)
5. Lưu lại

### Bước 3: Cấu Hình WSGI File
1. Trong "Web" tab, tìm "Code" section
2. Click vào WSGI file để edit
3. Thay thế nội dung bằng:

```python
import sys
import os

# Thay YOUR_USERNAME bằng tên tài khoản PythonAnywhere của bạn
path = '/home/YOUR_USERNAME/salary_app'
if path not in sys.path:
    sys.path.append(path)

os.environ.setdefault('FLASK_ENV', 'production')

from app import create_app

application = create_app('production')
```

Đặt `SECRET_KEY` trong file `.env` của project (bắt buộc ở chế độ production).
Tài khoản admin được tạo bằng lệnh `flask init-db` ở Bước 1, không tạo trong WSGI file.

4. Lưu file (Ctrl+S)

### Bước 4: Cấu Hình Virtual Environment
1. Trong "Web" tab, tìm "Virtualenv"
2. Nhập: `/home/YOUR_USERNAME/salary_app/venv`
3. Click checkmark
4. Chờ vài giây

### Bước 5: Cấu Hình Static Files
Trong "Web" tab, tìm "Static files" section:

Thêm mapping:
1. 
   - URL: `/static/`
   - Directory: `/home/YOUR_USERNAME/salary_app/app/static`

### Bước 6: Reload Web App
Click nút "Reload" (bên phải domain name)

### Bước 7: Truy Cập Ứng Dụng
Mở browser và truy cập:
```
https://YOUR_USERNAME.pythonanywhere.com
```

Đăng nhập với:
- Username: `admin`
- Password: mật khẩu do `flask init-db` sinh ra

## Cập Nhật Code Sau Này
```bash
cd ~/salary_app
git pull
source venv/bin/activate
pip install -r requirements.txt
# Rồi reload web app
```

## Các Lỗi Thường Gặp

| Lỗi | Giải Pháp |
|-----|----------|
| ModuleNotFoundError | Kiểm tra virtual environment path trong Web tab |
| 404 Static files | Kiểm tra Static files mapping, path phải đúng |
| Permission denied | `chmod 755 ~/salary_app -R` |
| Database error | Chạy lại: `python3 -c "from run import app, db; app.app_context().push(); db.create_all()"` |
| Application error | Xem PythonAnywhere error log |

## Xem Error Log
1. Mở "Web" tab
2. Scroll down tìm "Log files"
3. Click vào error log để xem lỗi chi tiết

## Domain Custom
Sau khi ứng dụng chạy ổn định, bạn có thể:
1. Mua domain riêng
2. Trong PythonAnywhere, cấu hình domain trong "Web" tab
3. Cấu hình DNS từ nhà cung cấp domain

## Tham Khảo
- https://help.pythonanywhere.com/pages/Flask
- https://help.pythonanywhere.com/pages/WebConsoles
- https://help.pythonanywhere.com/pages/PythonAnywhere101
