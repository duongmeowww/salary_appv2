from functools import wraps

from flask import Blueprint, abort, current_app, flash, redirect, render_template, request, send_file, url_for
from flask_login import current_user, login_required, login_user, logout_user
from sqlalchemy import func, or_
from sqlalchemy.orm import selectinload

from . import db
from .forms import AdminEmployeeForm, AdminResetPasswordForm, ChangePasswordForm, LoginForm, ProfileForm, UploadForm
from .models import Salary, User
from .utils import generate_sample_excel_stream, generate_salaries_excel, parse_salary_excel

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


def _available_periods(limit=None):
    """Trả về danh sách (year, month) các kỳ lương đang có, mới nhất trước."""
    query = (
        db.session.query(Salary.year, Salary.month)
        .distinct()
        .order_by(Salary.year.desc(), Salary.month.desc())
    )
    if limit:
        query = query.limit(limit)
    return query.all()


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
    avg_net = 0
    if latest_period is not None:
        year, month = latest_period
        period_label = 'Tháng {:02d}/{}'.format(month, year)
        period_total, period_employees = (
            db.session.query(func.coalesce(func.sum(Salary.net_salary), 0), func.count(Salary.id))
            .filter(Salary.year == year, Salary.month == month)
            .one()
        )
        if period_employees:
            avg_net = period_total / period_employees

    # Dữ liệu biểu đồ xu hướng 12 kỳ gần nhất
    chart_labels = []
    chart_totals = []
    chart_counts = []
    trend_periods = _available_periods(12)
    for year, month in reversed(trend_periods):
        total, count = (
            db.session.query(func.coalesce(func.sum(Salary.net_salary), 0), func.count(Salary.id))
            .filter(Salary.year == year, Salary.month == month)
            .one()
        )
        chart_labels.append('Tháng {:02d}/{}'.format(month, year))
        chart_totals.append(round(total))
        chart_counts.append(count)

    return render_template(
        'admin_dashboard.html',
        employee_count=employee_count,
        salary_count=salary_count,
        period_label=period_label,
        period_total=period_total,
        period_employees=period_employees,
        avg_net=round(avg_net),
        chart_labels=chart_labels,
        chart_totals=chart_totals,
        chart_counts=chart_counts,
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
            user = User(
                username=record['username'],
                full_name=record['full_name'],
                is_admin=False,
                department=record.get('department'),
                position=record.get('position'),
                phone=record.get('phone'),
                bank_name=record.get('bank_name'),
                bank_account=record.get('bank_account'),
            )
            user.set_password(record['username'])
            db.session.add(user)
            users[user.username] = user
        else:
            if record.get('full_name'):
                user.full_name = record['full_name']
            if record.get('department'):
                user.department = record['department']
            if record.get('position'):
                user.position = record['position']
            if record.get('phone'):
                user.phone = record['phone']
            if record.get('bank_name'):
                user.bank_name = record['bank_name']
            if record.get('bank_account'):
                user.bank_account = record['bank_account']

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
    period = (request.args.get('period') or '').strip()  # dạng "YYYY-MM" hoặc "YYYY-MM-ALL"

    query = User.query.filter_by(is_admin=False)
    if keyword:
        pattern = f'%{keyword}%'
        query = query.filter(or_(User.username.ilike(pattern), User.full_name.ilike(pattern)))

    # Lọc theo kỳ lương: lấy nhân viên có bản ghi trong kỳ được chọn
    if period:
        try:
            year_part, month_part = (period.split('-') + [None, None])[:2]
            year = int(year_part)
            month = int(month_part) if month_part else None
        except (ValueError, TypeError):
            year = None
            month = None
        if year:
            employee_ids = db.session.query(Salary.employee_id).filter(Salary.year == year)
            if month:
                employee_ids = employee_ids.filter(Salary.month == month)
            query = query.filter(User.id.in_(employee_ids))

    pagination = (
        query
        .options(selectinload(User.salaries))
        .order_by(User.username)
        .paginate(page=page, per_page=EMPLOYEES_PER_PAGE, error_out=False)
    )
    if page > 1 and not pagination.items:
        abort(404)

    periods = _available_periods()
    return render_template(
        'all_salaries.html',
        pagination=pagination,
        users=pagination.items,
        keyword=keyword,
        period=period,
        periods=periods,
    )


@bp.route('/download-template')
@login_required
def download_template():
    stream = generate_sample_excel_stream()
    return send_file(
        stream,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name='bang_luong_mau.xlsx',
    )


@bp.route('/admin/all-salaries/export')
@admin_required
def export_salaries():
    keyword = (request.args.get('q') or '').strip()
    period = (request.args.get('period') or '').strip()

    query = Salary.query.join(User).filter(User.is_admin == False)
    if keyword:
        pattern = f'%{keyword}%'
        query = query.filter(or_(User.username.ilike(pattern), User.full_name.ilike(pattern)))
    if period:
        try:
            year_part, month_part = (period.split('-') + [None, None])[:2]
            year = int(year_part)
            month = int(month_part) if month_part else None
        except (ValueError, TypeError):
            year = None
            month = None
        if year:
            query = query.filter(Salary.year == year)
            if month:
                query = query.filter(Salary.month == month)

    rows = query.order_by(Salary.year.desc(), Salary.month.desc(), User.username).all()
    export_rows = [
        {
            'username': salary.employee.username if salary.employee else '',
            'full_name': salary.employee.full_name if salary.employee else '',
            'department': salary.employee.department if salary.employee else '',
            'position': salary.employee.position if salary.employee else '',
            'month': salary.month,
            'year': salary.year,
            'basic_salary': salary.basic_salary,
            'allowance': salary.allowance,
            'deduction': salary.deduction,
            'net_salary': salary.net_salary,
        }
        for salary in rows
    ]

    stream = generate_salaries_excel(export_rows)
    name = 'bang_luong'
    if period:
        name += '_' + period
    return send_file(
        stream,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=f'{name}.xlsx',
    )


@bp.route('/admin/employees/<int:user_id>/salary')
@admin_required
def employee_salary_detail(user_id):
    employee = db.session.get(User, user_id)
    if not employee or employee.is_admin:
        abort(404)

    salaries = (
        Salary.query
        .filter_by(employee_id=employee.id)
        .order_by(Salary.year.desc(), Salary.month.desc())
        .all()
    )
    total_net = sum(s.net_salary or 0 for s in salaries)
    return render_template(
        'employee_salary_detail.html',
        employee=employee,
        salaries=salaries,
        total_net=total_net,
    )


@bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    profile_form = ProfileForm(obj=current_user)
    password_form = ChangePasswordForm()

    action = request.form.get('action')

    if action == 'update_profile' and profile_form.validate_on_submit():
        if current_user.is_admin and profile_form.full_name.data:
            current_user.full_name = profile_form.full_name.data.strip()
        current_user.phone = (profile_form.phone.data or '').strip()
        current_user.email = (profile_form.email.data or '').strip()
        if current_user.is_admin:
            current_user.department = (profile_form.department.data or '').strip()
            current_user.position = (profile_form.position.data or '').strip()
        current_user.bank_name = (profile_form.bank_name.data or '').strip()
        current_user.bank_account = (profile_form.bank_account.data or '').strip()
        db.session.commit()
        flash('Cập nhật thông tin cá nhân thành công!', 'success')
        return redirect(url_for('main.profile'))

    if action == 'change_password' and password_form.validate_on_submit():
        if not current_user.check_password(password_form.current_password.data):
            flash('Mật khẩu hiện tại không chính xác.', 'danger')
        else:
            current_user.set_password(password_form.new_password.data)
            db.session.commit()
            flash('Đổi mật khẩu thành công!', 'success')
            return redirect(url_for('main.profile'))

    return render_template(
        'profile.html',
        profile_form=profile_form,
        password_form=password_form,
    )


@bp.route('/admin/employees')
@admin_required
def employees_list():
    page = request.args.get('page', 1, type=int)
    keyword = (request.args.get('q') or '').strip()
    dept = (request.args.get('dept') or '').strip()

    query = User.query.filter_by(is_admin=False)
    if keyword:
        pattern = f'%{keyword}%'
        query = query.filter(
            or_(
                User.username.ilike(pattern),
                User.full_name.ilike(pattern),
                User.phone.ilike(pattern),
                User.department.ilike(pattern),
                User.position.ilike(pattern),
            )
        )
    if dept:
        query = query.filter(User.department == dept)

    departments = [
        d[0] for d in db.session.query(User.department).filter(
            User.is_admin == False, User.department.isnot(None), User.department != ''
        ).distinct().all()
    ]

    pagination = (
        query
        .options(selectinload(User.salaries))
        .order_by(User.username)
        .paginate(page=page, per_page=EMPLOYEES_PER_PAGE, error_out=False)
    )

    return render_template(
        'employees.html',
        pagination=pagination,
        employees=pagination.items,
        keyword=keyword,
        dept=dept,
        departments=departments,
    )


@bp.route('/admin/employees/add', methods=['GET', 'POST'])
@admin_required
def add_employee():
    form = AdminEmployeeForm()
    if form.validate_on_submit():
        username = form.username.data.strip()
        existing = User.query.filter_by(username=username).first()
        if existing:
            flash(f'Mã nhân viên "{username}" đã tồn tại trong hệ thống!', 'danger')
            return render_template('employee_form.html', form=form, is_edit=False)

        user = User(
            username=username,
            full_name=form.full_name.data.strip(),
            department=(form.department.data or '').strip(),
            position=(form.position.data or '').strip(),
            phone=(form.phone.data or '').strip(),
            email=(form.email.data or '').strip(),
            bank_name=(form.bank_name.data or '').strip(),
            bank_account=(form.bank_account.data or '').strip(),
            is_admin=False,
        )
        password = form.password.data.strip() if form.password.data else username
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash(f'Thêm nhân viên "{user.full_name}" ({user.username}) thành công!', 'success')
        return redirect(url_for('main.employees_list'))

    return render_template('employee_form.html', form=form, is_edit=False)


@bp.route('/admin/employees/<int:user_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_employee(user_id):
    employee = db.session.get(User, user_id)
    if not employee or employee.is_admin:
        abort(404)

    form = AdminEmployeeForm(obj=employee)
    reset_form = AdminResetPasswordForm()

    if request.method == 'POST' and request.form.get('action') == 'update_info':
        if form.validate_on_submit():
            # Check if username changed and clashes
            new_username = form.username.data.strip()
            if new_username != employee.username:
                clash = User.query.filter_by(username=new_username).first()
                if clash:
                    flash(f'Mã nhân viên "{new_username}" đã tồn tại!', 'danger')
                    return render_template('employee_form.html', form=form, reset_form=reset_form, is_edit=True, employee=employee)
                employee.username = new_username

            employee.full_name = form.full_name.data.strip()
            employee.department = (form.department.data or '').strip()
            employee.position = (form.position.data or '').strip()
            employee.phone = (form.phone.data or '').strip()
            employee.email = (form.email.data or '').strip()
            employee.bank_name = (form.bank_name.data or '').strip()
            employee.bank_account = (form.bank_account.data or '').strip()
            db.session.commit()
            flash(f'Đã cập nhật thông tin nhân viên {employee.full_name}!', 'success')
            return redirect(url_for('main.employees_list'))

    return render_template('employee_form.html', form=form, reset_form=reset_form, is_edit=True, employee=employee)


@bp.route('/admin/employees/<int:user_id>/reset-password', methods=['POST'])
@admin_required
def reset_employee_password(user_id):
    employee = db.session.get(User, user_id)
    if not employee or employee.is_admin:
        abort(404)

    new_password = (request.form.get('new_password') or '').strip()
    if not new_password:
        new_password = employee.username  # Reset về mã NV mặc định

    employee.set_password(new_password)
    db.session.commit()
    flash(f'Đã đặt lại mật khẩu cho nhân viên {employee.full_name} ({employee.username}) thành: "{new_password}"', 'success')
    return redirect(url_for('main.employees_list'))


@bp.route('/admin/employees/<int:user_id>/delete', methods=['POST'])
@admin_required
def delete_employee(user_id):
    employee = db.session.get(User, user_id)
    if not employee or employee.is_admin:
        abort(404)

    name = employee.full_name or employee.username
    db.session.delete(employee)
    db.session.commit()
    flash(f'Đã xóa nhân viên "{name}" và toàn bộ lịch sử lương liên quan.', 'info')
    return redirect(url_for('main.employees_list'))
