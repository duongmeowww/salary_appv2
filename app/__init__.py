import os
from datetime import date

from dotenv import load_dotenv
from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect

load_dotenv()

db = SQLAlchemy()
csrf = CSRFProtect()
login_manager = LoginManager()
login_manager.login_view = 'main.login'
login_manager.login_message = 'Vui lòng đăng nhập để tiếp tục.'
login_manager.login_message_category = 'info'


@login_manager.user_loader
def load_user(user_id):
    from .models import User
    return db.session.get(User, int(user_id))


def create_app(config_name=None):
    from config import get_config

    app = Flask(__name__)
    config_class = get_config(config_name)
    app.config.from_object(config_class)
    if hasattr(config_class, 'init_app'):
        config_class.init_app(app)

    db_uri = app.config['SQLALCHEMY_DATABASE_URI']
    if db_uri.startswith('sqlite:///') and ':memory:' not in db_uri:
        os.makedirs(os.path.dirname(db_uri[len('sqlite:///'):]), exist_ok=True)

    db.init_app(app)
    csrf.init_app(app)
    login_manager.init_app(app)

    @app.template_filter('money')
    def money(value):
        return '{:,.0f}'.format(value or 0)

    @app.template_filter('period')
    def period(salary):
        return 'Tháng {:02d}/{}'.format(salary.month, salary.year)

    @app.context_processor
    def inject_company():
        return {
            'company_name': app.config['COMPANY_NAME'],
            'company_slogan': app.config['COMPANY_SLOGAN'],
            'current_year': date.today().year,
        }

    from . import routes
    app.register_blueprint(routes.bp)

    from .cli import register_cli
    register_cli(app)

    from .errors import register_error_handlers
    register_error_handlers(app)

    return app
