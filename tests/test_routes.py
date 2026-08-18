from app.models import Salary, User
from tests.conftest import build_excel, login


def test_index_redirects_to_login(client):
    response = client.get('/')
    assert response.status_code == 302
    assert '/login' in response.headers['Location']


def test_protected_page_redirects_anonymous_user(client):
    response = client.get('/my-salary')
    assert response.status_code == 302
    assert '/login' in response.headers['Location']


def test_login_success_and_failure(client, admin):
    assert 'Đăng nhập thành công' in login(client, 'admin', 'admin123').get_data(as_text=True)
    client.get('/logout')
    assert 'Sai mã nhân viên' in login(client, 'admin', 'wrong').get_data(as_text=True)


def test_employee_cannot_access_admin_pages(client, app):
    from app import db

    employee = User(username='NV001', full_name='Nhân viên', is_admin=False)
    employee.set_password('NV001')
    db.session.add(employee)
    db.session.commit()

    login(client, 'NV001', 'NV001')
    response = client.get('/admin/all-salaries', follow_redirects=True)
    assert 'không có quyền' in response.get_data(as_text=True)


def upload_excel(client, rows):
    return client.post(
        '/upload',
        data={'file': (build_excel(rows), 'salary.xlsx')},
        content_type='multipart/form-data',
        follow_redirects=True,
    )


def test_upload_creates_users_and_salaries(client, admin):
    login(client, 'admin', 'admin123')
    response = upload_excel(client, [
        ['NV001', 'Nguyễn Văn A', 1, 2024, 10000000, 1000000, 500000, 10500000],
    ])
    assert 'thành công' in response.get_data(as_text=True)

    user = User.query.filter_by(username='NV001').first()
    assert user is not None and user.check_password('NV001')
    assert Salary.query.count() == 1


def test_upload_twice_updates_instead_of_duplicating(client, admin):
    login(client, 'admin', 'admin123')
    upload_excel(client, [['NV001', 'A', 1, 2024, 1000, 0, 0, 1000]])
    upload_excel(client, [['NV001', 'A', 1, 2024, 2000, 0, 0, 2000]])

    salaries = Salary.query.all()
    assert len(salaries) == 1
    assert salaries[0].net_salary == 2000


def test_upload_invalid_file_shows_error(client, admin):
    login(client, 'admin', 'admin123')
    response = client.post(
        '/upload',
        data={'file': (build_excel([], columns=['Mã nhân viên']), 'bad.xlsx')},
        content_type='multipart/form-data',
        follow_redirects=True,
    )
    assert 'Lỗi xử lý file' in response.get_data(as_text=True)
    assert User.query.filter_by(is_admin=False).count() == 0


def test_all_salaries_page_renders(client, admin):
    login(client, 'admin', 'admin123')
    upload_excel(client, [['NV001', 'Nguyễn Văn A', 1, 2024, 10000000, 0, 0, 10000000]])
    response = client.get('/admin/all-salaries')
    assert response.status_code == 200
    assert '10,000,000' in response.get_data(as_text=True)


def test_all_salaries_search_filters_employees(client, admin):
    login(client, 'admin', 'admin123')
    upload_excel(client, [
        ['NV001', 'Nguyễn Văn A', 1, 2024, 1000, 0, 0, 1000],
        ['NV002', 'Trần Thị B', 1, 2024, 2000, 0, 0, 2000],
    ])

    body = client.get('/admin/all-salaries?q=NV002').get_data(as_text=True)
    assert 'NV002' in body
    assert 'NV001' not in body


def test_admin_dashboard_shows_statistics(client, admin):
    login(client, 'admin', 'admin123')
    upload_excel(client, [['NV001', 'Nguyễn Văn A', 3, 2024, 9000000, 0, 0, 9000000]])

    body = client.get('/admin').get_data(as_text=True)
    assert 'Tháng 03/2024' in body
    assert '9,000,000' in body


def test_not_found_page(client):
    response = client.get('/khong-ton-tai')
    assert response.status_code == 404
