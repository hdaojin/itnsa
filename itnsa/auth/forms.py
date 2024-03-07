from flask_wtf import FlaskForm
from wtforms import StringField, RadioField, PasswordField, SubmitField, EmailField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError 

import re


class RegisterForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired(), Length(min=3, max=120, message='用户名长度必须介于 3 到 120 个字符之间。')], description="用户名长度不能少于3个字符, 且只能包含字母、数字、短横杠和下划线",
                           render_kw={'placeholder': '用于登录的用户名'})
    password = PasswordField('密码', validators=[DataRequired(), Length(min=8, max=512),
                                               EqualTo('confirm', message='两次输入的密码不一致')],
                                     description="密码长度不能少于8个字符, 且必须包含数字、小写字母、大写字母、特殊字符"
                            )
    confirm = PasswordField('确认密码', validators=[DataRequired(), Length(min=8, max=512)])
    real_name = StringField('真实姓名', validators=[DataRequired(), Length(min=2, max=120)])
    roles = RadioField('角色', validators=[DataRequired()])  # Dynamic choices in view function
    # email = StringField('邮箱', validators=[DataRequired(), Length(min=5, max=50)])
    email = EmailField('邮箱', validators=[DataRequired(), Length(min=5, max=64)])
    # recaptcha = RecaptchaField()
    submit = SubmitField('注册')
   
    # The `validate_password` method is a custom validator that WTForms will automatically call when you invoke `form.validate()`. 
    # WTForms 会自动寻找形式为 validate_<fieldname> 的方法作为特定字段的额外验证器。例如，如果你有一个名为 email 的字段，WTForms 会自动调用一个名为 validate_email 的方法（如果存在）作为该字段的额外验证步骤。
    def validate_username(self, field):
        if not re.match(r'^[a-zA-Z0-9_-]{3,120}$', field.data):
            raise ValidationError('用户名只能包含字母、数字、短横杠和下划线')

    def validate_password(self, field):
        password_data = field.data
        errors = []
        if not re.search(r'[a-z]', password_data):
            errors.append('密码必须包含小写字母')
        if not re.search(r'[A-Z]', password_data):
            errors.append('密码必须包含大写字母')
        if not re.search(r'[0-9]', password_data):
            errors.append('密码必须包含数字')
        if not re.search(r'[^a-zA-Z0-9]', password_data):
            errors.append('密码必须包含特殊字符')
        if re.search(r'[\s]', password_data):
            errors.append('密码不能包含空格')
        if re.search(r'[\u4e00-\u9fa5]', password_data) or re.search(r'[\uFF00-\uFFEF]', password_data) or re.search(r'[\u3000]', password_data):
            errors.append('密码不能包含中文字符或全角字符')
        if self.username.data and password_data.lower() == self.username.data.lower():
            errors.append('密码不能与用户名相同')
        if password_data.lower() in [
                                        'abc123!@#', 'abc123$%^', 'abc123&*(', 'abc123!@#$', 'abc123!@#$%^', 
                                        'password!@#', 'password!@#$', 'password!@#$', 'password!@#$%^', 'password!@#$%^&',
                                        'skills39!', 'skills39!!', 'skills39!!!',
                                        'skill39!', 'skill39!!', 'skill39!!!']:
            errors.append('密码太简单了')

        if errors:
            raise ValidationError(' '.join(errors))


class LoginForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired(), Length(min=3, max=120)],
                           render_kw={'placeholder': '请输入用户名'})
    password = PasswordField('密码', validators=[DataRequired(), Length(min=8, max=120)],
                            render_kw={'placeholder': '请输入密码'}
                            )
    remember_me = RadioField('记住我', choices=[('1', '是'), ('0', '否')], validators=[DataRequired()], default='0')
    # recaptcha = RecaptchaField()
    submit = SubmitField('登录')



