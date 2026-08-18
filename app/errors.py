from flask import render_template

from . import db


def register_error_handlers(app):
    @app.errorhandler(403)
    def forbidden(error):
        return render_template('error.html', code=403, message='Bạn không có quyền truy cập trang này.'), 403

    @app.errorhandler(404)
    def not_found(error):
        return render_template('error.html', code=404, message='Không tìm thấy trang.'), 404

    @app.errorhandler(413)
    def too_large(error):
        max_mb = app.config['MAX_CONTENT_LENGTH'] // (1024 * 1024)
        return render_template('error.html', code=413, message=f'File tải lên vượt quá {max_mb}MB.'), 413

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('error.html', code=500, message='Có lỗi xảy ra, vui lòng thử lại sau.'), 500
