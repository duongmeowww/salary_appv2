import os
from datetime import timedelta

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_SQLITE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'instance', 'salaries.db')


def _int_env(name, default):
    value = os.environ.get(name)
    if not value:
        return default
    try:
        return int(value)
    except ValueError:
        return default


class Config:
    """Cấu hình cơ bản"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    COMPANY_NAME = os.environ.get('COMPANY_NAME') or 'Công ty May mặc'
    COMPANY_SLOGAN = os.environ.get('COMPANY_SLOGAN') or 'Hệ thống quản lý lương công nhân'
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI') or DEFAULT_SQLITE_URI
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAX_CONTENT_LENGTH = _int_env('MAX_CONTENT_LENGTH', 16 * 1024 * 1024)
    PERMANENT_SESSION_LIFETIME = timedelta(days=_int_env('PERMANENT_SESSION_LIFETIME', 7))
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    DEBUG = False
    TESTING = False


class DevelopmentConfig(Config):
    """Cấu hình cho Development"""
    DEBUG = True


class ProductionConfig(Config):
    """Cấu hình cho Production (PythonAnywhere)"""
    SESSION_COOKIE_SECURE = True

    @staticmethod
    def init_app(app):
        if app.config['SECRET_KEY'] == 'dev-secret-key-change-in-production':
            raise RuntimeError(
                'SECRET_KEY phải được đặt qua biến môi trường khi chạy production. '
                'Tạo bằng: python -c "import secrets; print(secrets.token_hex(32))"'
            )


class TestingConfig(Config):
    """Cấu hình cho Testing"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig,
}


def get_config(env=None):
    if env is None:
        env = os.environ.get('FLASK_ENV', 'development')
    return config.get(env, DevelopmentConfig)
