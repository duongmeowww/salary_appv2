import os
import sys

# Thư mục chứa project (không hardcode đường dẫn tuyệt đối)
project_path = os.path.dirname(os.path.abspath(__file__))
if project_path not in sys.path:
    sys.path.insert(0, project_path)

from app import create_app, db  # noqa: E402
from app.cli import create_admin  # noqa: E402
from app.models import ensure_schema_updates  # noqa: E402

application = create_app(os.environ.get('FLASK_ENV', 'production'))
app = application

# Tạo bảng và tài khoản admin mặc định nếu chưa có
with application.app_context():
    db.create_all()
    ensure_schema_updates()
    admin_password = os.environ.get('ADMIN_PASSWORD', 'admin123')
    create_admin(password=admin_password)
