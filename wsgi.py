import os
import sys

# Thư mục chứa project (không hardcode đường dẫn tuyệt đối)
project_path = os.path.dirname(os.path.abspath(__file__))
if project_path not in sys.path:
    sys.path.insert(0, project_path)

from app import create_app, db  # noqa: E402

application = create_app(os.environ.get('FLASK_ENV', 'production'))

# Tạo bảng nếu chưa có. Tài khoản admin được tạo bằng lệnh: flask init-db
with application.app_context():
    db.create_all()
