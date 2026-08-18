from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileRequired, FileField
from wtforms import PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, EqualTo, Length, Optional


class LoginForm(FlaskForm):
    username = StringField('Mã nhân viên', validators=[DataRequired(message='Vui lòng nhập mã nhân viên.')])
    password = PasswordField('Mật khẩu', validators=[DataRequired(message='Vui lòng nhập mật khẩu.')])
    submit = SubmitField('Đăng nhập')


class UploadForm(FlaskForm):
    file = FileField('Chọn file Excel', validators=[
        FileRequired(message='Vui lòng chọn file Excel!'),
        FileAllowed(['xlsx', 'xls'], 'Chỉ chấp nhận file Excel (.xlsx, .xls)!')
    ])
    submit = SubmitField('Tải lên và xử lý')


class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Mật khẩu hiện tại', validators=[
        DataRequired(message='Vui lòng nhập mật khẩu hiện tại.')
    ])
    new_password = PasswordField('Mật khẩu mới', validators=[
        DataRequired(message='Vui lòng nhập mật khẩu mới.'),
        Length(min=4, message='Mật khẩu mới phải có ít nhất 4 ký tự.')
    ])
    confirm_password = PasswordField('Xác nhận mật khẩu mới', validators=[
        DataRequired(message='Vui lòng xác nhận mật khẩu mới.'),
        EqualTo('new_password', message='Mật khẩu xác nhận không trùng khớp.')
    ])
    submit = SubmitField('Đổi mật khẩu')


class ProfileForm(FlaskForm):
    full_name = StringField('Họ và tên', validators=[Optional()])
    phone = StringField('Số điện thoại', validators=[Optional(), Length(max=20)])
    email = StringField('Email', validators=[Optional(), Length(max=100)])
    department = StringField('Phòng ban / Xưởng', validators=[Optional(), Length(max=100)])
    position = StringField('Chức vụ / Vị trí', validators=[Optional(), Length(max=100)])
    bank_name = StringField('Tên ngân hàng', validators=[Optional(), Length(max=100)])
    bank_account = StringField('Số tài khoản ngân hàng', validators=[Optional(), Length(max=50)])
    submit = SubmitField('Lưu thông tin')


class AdminEmployeeForm(FlaskForm):
    username = StringField('Mã nhân viên', validators=[DataRequired(message='Vui lòng nhập mã nhân viên.')])
    full_name = StringField('Họ và tên', validators=[DataRequired(message='Vui lòng nhập họ và tên.')])
    department = StringField('Phòng ban / Xưởng', validators=[Optional(), Length(max=100)])
    position = StringField('Chức vụ / Vị trí', validators=[Optional(), Length(max=100)])
    phone = StringField('Số điện thoại', validators=[Optional(), Length(max=20)])
    email = StringField('Email', validators=[Optional(), Length(max=100)])
    bank_name = StringField('Tên ngân hàng', validators=[Optional(), Length(max=100)])
    bank_account = StringField('Số tài khoản ngân hàng', validators=[Optional(), Length(max=50)])
    password = PasswordField('Mật khẩu ban đầu (bỏ trống để lấy theo Mã NV)', validators=[Optional()])
    submit = SubmitField('Lưu nhân viên')


class AdminResetPasswordForm(FlaskForm):
    new_password = PasswordField('Mật khẩu mới', validators=[
        DataRequired(message='Vui lòng nhập mật khẩu mới.'),
        Length(min=4, message='Mật khẩu phải có ít nhất 4 ký tự.')
    ])
    submit = SubmitField('Cập nhật mật khẩu')
