from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from . import db


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    password = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(100))
    is_admin = db.Column(db.Boolean, default=False, nullable=False, index=True)

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
