from flask_login import UserMixin
from sqlalchemy import inspect, text
from werkzeug.security import check_password_hash, generate_password_hash

from . import db


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    password = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(100))
    is_admin = db.Column(db.Boolean, default=False, nullable=False, index=True)
    phone = db.Column(db.String(20), nullable=True)
    email = db.Column(db.String(100), nullable=True)
    department = db.Column(db.String(100), nullable=True)
    position = db.Column(db.String(100), nullable=True)
    bank_name = db.Column(db.String(100), nullable=True)
    bank_account = db.Column(db.String(50), nullable=True)

    salaries = db.relationship(
        'Salary',
        backref='employee',
        lazy=True,
        cascade='all, delete-orphan',
        order_by='Salary.year.desc(), Salary.month.desc()',
    )

    def set_password(self, raw_password):
        self.password = generate_password_hash(raw_password)

    def check_password(self, raw_password):
        return check_password_hash(self.password, raw_password)


def ensure_schema_updates():
    """Tự động kiểm tra và thêm các cột mới nếu DB đã tồn tại trước đó."""
    try:
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        user_table = 'user' if 'user' in tables else ('users' if 'users' in tables else None)
        if not user_table:
            return

        existing_columns = {col['name'] for col in inspector.get_columns(user_table)}
        new_columns = [
            ('phone', 'VARCHAR(20)'),
            ('email', 'VARCHAR(100)'),
            ('department', 'VARCHAR(100)'),
            ('position', 'VARCHAR(100)'),
            ('bank_name', 'VARCHAR(100)'),
            ('bank_account', 'VARCHAR(50)'),
        ]

        with db.engine.connect() as conn:
            for col_name, col_type in new_columns:
                if col_name not in existing_columns:
                    try:
                        if db.engine.name == 'postgresql':
                            conn.execute(text(f'ALTER TABLE "{user_table}" ADD COLUMN IF NOT EXISTS {col_name} {col_type};'))
                        else:
                            conn.execute(text(f'ALTER TABLE {user_table} ADD COLUMN {col_name} {col_type};'))
                        conn.commit()
                    except Exception:
                        pass
    except Exception:
        pass


class Salary(db.Model):
    __table_args__ = (
        db.UniqueConstraint('employee_id', 'month', 'year', name='uq_salary_employee_period'),
        db.Index('ix_salary_employee_period', 'employee_id', 'year', 'month'),
    )

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    month = db.Column(db.Integer, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    basic_salary = db.Column(db.Float, default=0.0)
    allowance = db.Column(db.Float, default=0.0)
    deduction = db.Column(db.Float, default=0.0)
    net_salary = db.Column(db.Float, default=0.0)
