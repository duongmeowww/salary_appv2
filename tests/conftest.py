import io

import pytest
from openpyxl import Workbook

from app import create_app, db
from app.models import User
from app.utils import REQUIRED_COLUMNS


@pytest.fixture
def app():
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def admin(app):
    user = User(username='admin', full_name='Quản trị viên', is_admin=True)
    user.set_password('admin123')
    db.session.add(user)
    db.session.commit()
    return user


def login(client, username, password):
    return client.post(
        '/login',
        data={'username': username, 'password': password},
        follow_redirects=True,
    )


def build_excel(rows, columns=REQUIRED_COLUMNS):
    workbook = Workbook()
    sheet = workbook.active
    sheet.append(list(columns))
    for row in rows:
        sheet.append(list(row))
    stream = io.BytesIO()
    workbook.save(stream)
    stream.seek(0)
    return stream
