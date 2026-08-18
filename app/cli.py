import os
import secrets

import click

from . import db
from .models import User


def create_admin(username='admin', password=None, full_name='Quản trị viên'):
    """Tạo tài khoản admin nếu chưa tồn tại. Trả về (user, raw_password) hoặc (user, None)."""
    user = User.query.filter_by(username=username).first()
    if user is not None:
        return user, None

    raw_password = password or os.environ.get('ADMIN_PASSWORD') or 'admin123'
    user = User(username=username, full_name=full_name, is_admin=True)
    user.set_password(raw_password)
    db.session.add(user)
    db.session.commit()
    return user, raw_password


def register_cli(app):
    @app.cli.command('init-db')
    @click.option('--admin-password', default=None, help='Mật khẩu cho tài khoản admin đầu tiên.')
    def init_db(admin_password):
        """Tạo bảng và tài khoản admin đầu tiên."""
        db.create_all()
        _, raw_password = create_admin(password=admin_password)
        if raw_password:
            click.echo(f'Đã tạo tài khoản admin: username=admin, password={raw_password}')
        else:
            click.echo('Tài khoản admin đã tồn tại.')

    @app.cli.command('reset-password')
    @click.argument('username')
    @click.argument('password')
    def reset_password(username, password):
        """Đặt lại mật khẩu cho một tài khoản."""
        user = User.query.filter_by(username=username).first()
        if user is None:
            raise click.ClickException(f'Không tìm thấy tài khoản "{username}".')
        user.set_password(password)
        db.session.commit()
        click.echo(f'Đã đặt lại mật khẩu cho {username}.')
