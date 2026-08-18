import os

from app import create_app, db
from app.models import Salary, User

app = create_app()


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Salary': Salary}


if __name__ == '__main__':
    with app.app_context():
        db.create_all()

    app.run(
        debug=app.config['DEBUG'],
        host=os.environ.get('FLASK_HOST', '127.0.0.1'),
        port=int(os.environ.get('FLASK_PORT', 5000)),
    )
