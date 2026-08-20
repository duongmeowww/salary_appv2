# Ứng Dụng Quản Lý Lương Nhân Viên (Salary Management App)

Ứng dụng Flask để quản lý lương nhân viên với tính năng upload file Excel, xem lương, và dashboard admin.

## Tính Năng

- 🔐 **Xác Thực**: Đăng nhập an toàn với mã nhân viên
- 📊 **Dashboard Admin**: Xem tổng quát lương của tất cả nhân viên, biểu đồ xu hướng 12 kỳ gần nhất
- 👤 **Trang Nhân Viên**: Xem lương cá nhân, cập nhật hồ sơ, đổi mật khẩu
- 📤 **Upload Excel**: Kéo-thả file, hỗ trợ định dạng số tiền kiểu VN (8.500.000 / 8,5 / 1 000 000)
- 📋 **Bảng lương tổng hợp**: Lọc theo từ khoá, lọc theo kỳ lương, **xuất Excel**
- 👁️ **Chi tiết lương nhân viên**: Xem tổng hợp và **in bảng lương**
- 💾 **Database**: Lưu trữ dữ liệu an toàn với SQLAlchemy

## Yêu Cầu

- Python 3.8+
- pip

## Cài Đặt Cục Bộ

### 1. Clone/Download Project
```bash
git clone <repository_url>
cd salary_app
```

### 2. Tạo Virtual Environment
```bash
python -m venv venv

# Trên Windows
venv\Scripts\activate

# Trên Linux/Mac
source venv/bin/activate
```

### 3. Cài Đặt Dependencies
```bash
pip install -r requirements.txt
```

### 4. Khởi Tạo Database và Tài Khoản Admin
```bash
export FLASK_APP=run.py
flask init-db                       # sinh mật khẩu ngẫu nhiên và in ra màn hình
flask init-db --admin-password ...  # hoặc tự chọn mật khẩu
```

Đổi mật khẩu bất kỳ tài khoản nào:
```bash
flask reset-password NV001 mat-khau-moi
```

### 5. Chạy Ứng Dụng
```bash
python run.py
```

Ứng dụng sẽ chạy tại: http://localhost:5000

### 6. Đăng Nhập
- **Username**: admin
- **Password**: mật khẩu do `flask init-db` sinh ra (hoặc biến môi trường `ADMIN_PASSWORD`)

### 7. Chạy Test
```bash
pip install -r requirements-dev.txt
pytest
```

## Cấu Trúc Thư Mục

```
salary_app/
├── app/                          # Thư mục ứng dụng
│   ├── __init__.py              # Khởi tạo Flask app
│   ├── models.py                # Database models
│   ├── routes.py                # Routes/Views
│   ├── forms.py                 # WTForms
│   ├── utils.py                 # Utility functions
│   ├── static/                  # CSS, JS, images
│   │   ├── css/
│   │   └── js/
│   └── templates/               # HTML templates
│       ├── base.html
│       ├── login.html
│       ├── admin_dashboard.html
│       ├── employee_salary.html
│       ├── employee_salary_detail.html
│       ├── all_salaries.html
│       ├── employees.html
│       ├── employee_form.html
│       ├── profile.html
│       ├── upload.html
│       └── error.html
├── instance/                     # Instance folder (database)
│   └── salaries.db
├── tests/                        # Unit test (pytest)
├── run.py                        # Entry point
├── wsgi.py                       # WSGI config cho PythonAnywhere
├── config.py                     # Configuration
├── requirements.txt              # Dependencies
├── DEPLOYMENT_GUIDE.md          # Hướng dẫn triển khai
└── README.md                     # File này
```

## File Quan Trọng

### run.py
Entry point của ứng dụng cho môi trường development.

### config.py
Cấu hình cho các môi trường khác nhau (development, production, testing).

### wsgi.py
File cấu hình WSGI cho PythonAnywhere. Đây là file mà web server sẽ gọi.

### app/models.py
Database models:
- **User**: Lưu trữ thông tin nhân viên
- **Salary**: Lưu trữ lương của nhân viên

### app/routes.py
Các route của ứng dụng:
- `/login`: Trang đăng nhập
- `/admin`: Dashboard admin
- `/my-salary`: Trang xem lương nhân viên (nhân viên)
- `/admin/all-salaries`: Bảng lương tổng hợp (admin)
- `/admin/all-salaries/export`: Xuất bảng lương ra Excel (admin)
- `/admin/employees`: Quản lý danh sách nhân viên (admin)
- `/admin/employees/<id>/salary`: Chi tiết + in lương nhân viên (admin)
- `/admin/employees/add|edit|delete|reset-password`: CRUD nhân viên (admin)
- `/upload`: Trang upload file Excel (admin)
- `/profile`: Hồ sơ cá nhân + đổi mật khẩu
- `/download-template`: Tải file Excel mẫu
- `/logout`: Đăng xuất

## Triển Khai lên PythonAnywhere

Xem chi tiết trong file `DEPLOYMENT_GUIDE.md`

Tóm tắt:
1. Tạo tài khoản tại https://www.pythonanywhere.com
2. Upload code lên PythonAnywhere
3. Tạo virtual environment
4. Cấu hình Web app
5. Chỉnh sửa WSGI file
6. Reload app

## Thay Đổi SECRET_KEY

Bước quan trọng cho bảo mật:

```python
python -c "import secrets; print(secrets.token_hex(32))"
```

Copy kết quả và cập nhật vào file `.env` (biến `SECRET_KEY`). Ở chế độ production, ứng dụng sẽ báo lỗi nếu `SECRET_KEY` chưa được đặt.

## Tùy Chỉnh Thương Hiệu

Tên công ty và slogan hiển thị trên header, footer và trang đăng nhập được lấy từ `.env`:

```
COMPANY_NAME=Công ty May mặc ABC
COMPANY_SLOGAN=Hệ thống quản lý lương công nhân
```

## Database

Ứng dụng sử dụng SQLite mặc định, lưu tại `instance/salaries.db`.

Để reset database:
```bash
rm instance/salaries.db
flask init-db  # Sẽ tạo database mới
```

Có thể dùng MySQL/PostgreSQL bằng cách đặt biến môi trường `SQLALCHEMY_DATABASE_URI`.

> Lưu ý khi nâng cấp từ phiên bản cũ: bảng `salary` nay có ràng buộc duy nhất theo
> (nhân viên, tháng, năm). Nếu database cũ đang có bản ghi trùng, cần xoá bản ghi trùng
> trước khi tạo lại schema.

## Tính Năng Excel Upload

File Excel phải có các cột sau (theo đúng thứ tự):
1. Mã nhân viên (Employee ID)
2. Họ tên (Full Name)
3. Tháng (Month)
4. Năm (Year)
5. Lương cơ bản (Basic Salary)
6. Phụ cấp (Allowance)
7. Khấu trừ (Deduction)
8. Lương thực nhận (Net Salary)

File Excel được xử lý bởi hàm `parse_salary_excel()` trong `app/utils.py` (đọc trực tiếp
từ luồng upload bằng openpyxl, không ghi file tạm lên đĩa). Upload lại cùng một kỳ lương sẽ
cập nhật bản ghi cũ thay vì tạo bản ghi trùng.

Các cột số tiền chấp nhận nhiều định dạng nhập liệu: `8500000`, `8.500.000`, `8,5` (triệu),
`8 500 000`, kèm hoặc không kèm chữ "đ".

## Khắc Phục Sự Cố

### Lỗi ModuleNotFoundError
```bash
pip install -r requirements.txt
```

### Database không tạo được
```bash
rm instance/salaries.db
flask init-db
```

### Port 5000 đã được sử dụng
```bash
python run.py --port 8000
```

### Lỗi CSRF
Đảm bảo SECRET_KEY được cấu hình đúng trong `config.py`

## Bảo Mật

- ✅ Mật khẩu được hash bằng Werkzeug
- ✅ CSRF protection bằng Flask-WTF
- ✅ Session management bằng Flask-Login
- ✅ Kiểm tra quyền admin trên các route nhạy cảm
- ✅ Không còn mật khẩu admin mặc định trong source code
- ⚠️ Mật khẩu mặc định của nhân viên mới là mã nhân viên — nên yêu cầu đổi sau lần đăng nhập đầu

## Phát Triển Tiếp

- [ ] Xuất phiếu lương dạng PDF cho từng nhân viên
- [ ] Gửi email thông báo lương
- [ ] Role-based access control chi tiết hơn

## Liên Hệ

Nếu có vấn đề hoặc câu hỏi, hãy tạo issue trên GitHub.

## License

MIT License - xem LICENSE file để chi tiết
