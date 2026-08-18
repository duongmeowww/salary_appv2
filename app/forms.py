from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired

class LoginForm(FlaskForm):
    username = StringField('Mã nhân viên', validators=[DataRequired()])
    password = PasswordField('Mật khẩu', validators=[DataRequired()])
    submit = SubmitField('Đăng nhập')

class UploadForm(FlaskForm):
    file = FileField('Chọn file Excel', validators=[
        FileRequired(),
        FileAllowed(['xlsx', 'xls'], 'Chỉ chấp nhận file Excel!')
    ])
    submit = SubmitField('Tải lên và xử lý')