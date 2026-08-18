from functools import wraps

from flask import Blueprint, abort, current_app, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from sqlalchemy import func, or_
from sqlalchemy.orm import selectinload

from . import db
from .forms import LoginForm, UploadForm
from .models import Salary, User
from .utils import parse_salary_excel

bp = Blueprint('main', __name__)

EMPLOYEES_PER_PAGE = 20


def admin_required(view):
    @wraps(view)
    @login_required
    def wrapper(*args, **kwargs):
        if not current_user.is_admin:
            flash('Bạn không có quyền truy cập.', 'danger')
            return redirect(url_for('main.employee_salary'))
        return view(*args, **kwargs)
    return wrapper


def _home_url():
    return url_for('main.admin_dashboard' if current_user.is_admin else 'main.employee_salary')


@bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(_home_url())
    return redirect(url_for('main.login'))


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(_home_url())

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data.strip()).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash('Đăng nhập thành công!', 'success')
            return redirect(_home_url())
        flash('Sai mã nhân viên hoặc mật khẩu.', 'danger')
    return render_template('login.html', form=form)


@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Đã đăng xuất.', 'info')
    return redirect(url_for('main.login'))


@bp.route('/admin')
@admin_required
def admin_dashboard():
    employee_count = User.query.filter_by(is_admin=False).count()
    salary_count = Salary.query.count()

    latest_period = (
        db.session.query(Salary.year, Salary.month)
        .order_by(Salary.year.desc(), Salary.month.desc())
        .first()
    )
    period_label = None
    period_total = 0
    period_employees = 0
    if latest_period is not None:
        year, month = latest_period
        period_label = 'Tháng {:02d}/{}'.format(month, year)
        period_total, period_employees = (
            db.session.query(func.coalesce(func.sum(Salary.net_salary), 0), func.count(Salary.id))
            .filter(Salary.year == year, Salary.month == month)
            .one()
        )

    return render_template(
        'admin_dashboard.html',
        employee_count=employee_count,
        salary_count=salary_count,
        period_label=period_label,
        period_total=period_total,
        period_employees=period_employees,
    )


def _save_records(records):
    """Ghi dữ liệu lương vào DB: tạo nhân viên mới nếu chưa có và upsert theo (nhân viên, tháng, năm)."""
    usernames = {record['username'] for record in records}
    users = {
        user.username: user
        for user in User.query.filter(User.username.in_(usernames)).all()
    }

    for record in records:
        user = users.get(record['username'])
        if user is None:
            user = User(username=record['username'], full_name=record['full_name'], is_admin=False)
            user.set_password(record['username'])
            db.session.add(user)
            users[user.username] = user
        elif record['full_name']:
            user.full_name = record['full_name']

    db.session.flush()

    existing = {
        (salary.employee_id, salary.month, salary.year): salary
        for salary in Salary.query.filter(
            Salary.employee_id.in_([user.id for user in users.values()])
        ).all()
    }

    for record in records:
        user = users[record['username']]
        key = (user.id, record['month'], record['year'])
        salary = existing.get(key)
        if salary is None:
            salary = Salary(employee_id=user.id, month=record['month'], year=record['year'])
            db.session.add(salary)
            existing[key] = salary
        salary.basic_salary = record['basic_salary']
        salary.allowance = record['allowance']
        salary.deduction = record['deduction']
        salary.net_salary = record['net_salary']

    db.session.commit()


@bp.route('/upload', methods=['GET', 'POST'])
@admin_required
def upload():
    form = UploadForm()
    if form.validate_on_submit():
        try:
            records = parse_salary_excel(form.file.data.stream)
        except ValueError as error:
            flash(f'Lỗi xử lý file: {error}', 'danger')
            return render_template('upload.html', form=form)
        except Exception:
            current_app.logger.exception('Không đọc được file Excel')
            flash('Không đọc được file Excel. Vui lòng kiểm tra lại định dạng file.', 'danger')
            return render_template('upload.html', form=form)

        if not records:
            flash('File không có dòng dữ liệu nào.', 'warning')
            return render_template('upload.html', form=form)

        try:
            _save_records(records)
        except Exception:
            db.session.rollback()
            flash('Lỗi khi lưu dữ liệu vào cơ sở dữ liệu.', 'danger')
            return render_template('upload.html', form=form)

        flash(f'Đã xử lý {len(records)} dòng dữ liệu thành công!', 'success')
        return redirect(url_for('main.upload'))

    return render_template('upload.html', form=form)


@bp.route('/my-salary')
@login_required
def employee_salary():
    salaries = (
        Salary.query
        .filter_by(employee_id=current_user.id)
        .order_by(Salary.year.desc(), Salary.month.desc())
        .all()
    )
    return render_template('employee_salary.html', salaries=salaries)


@bp.route('/admin/all-salaries')
@admin_required
def all_salaries():
    page = request.args.get('page', 1, type=int)
    keyword = (request.args.get('q') or '').strip()

    query = User.query.filter_by(is_admin=False)
    if keyword:
        pattern = f'%{keyword}%'
        query = query.filter(or_(User.username.ilike(pattern), User.full_name.ilike(pattern)))

    pagination = (
        query
        .options(selectinload(User.salaries))
        .order_by(User.username)
        .paginate(page=page, per_page=EMPLOYEES_PER_PAGE, error_out=False)
    )
    if page > 1 and not pagination.items:
        abort(404)
    return render_template(
        'all_salaries.html',
        pagination=pagination,
        users=pagination.items,
        keyword=keyword,
    )
