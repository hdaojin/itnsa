from typing import Any
from flask_wtf import FlaskForm
from wtforms import StringField, RadioField, PasswordField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError

from datetime import datetime

class RegisterForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired(), Length(min=3, max=120)],
                           render_kw={'placeholder': '请使用姓名拼音全拼'})
    password = PasswordField('密码', validators=[DataRequired(), Length(min=8, max=512),
                                               EqualTo('confirm', message='两次输入的密码不一致')],
                                     description="密码长度不能少于8个字符, 且必须包含数字、小写字母、大写字母、特殊字符"
                            )
    confirm = PasswordField('确认密码', validators=[DataRequired(), Length(min=8, max=512)])
    
    real_name = StringField('真实姓名', validators=[DataRequired(), Length(min=2, max=120)])
    role = RadioField('角色', choices=[('competitor', '选手'), ('coach', '教练')], validators=[DataRequired()], default='competitor')
    email = StringField('邮箱', validators=[DataRequired(), Length(min=5, max=50)])
    # recaptcha = RecaptchaField()
   
    # The `validate_password` method is a custom validator that WTForms will automatically call when you invoke `form.validate()`. 
    def validate_password(form, field):
        sample_password = [
            '12345678',
            'skills',
            'abc123',
            'hello',
            'password',
            'pass'
        ]
        passord = field.data
        if len(passord) < 8:
            raise ValidationError('密码长度不能少于8个字符') 
        
        # Check for the presence of digits, uppercase and lowercase characters, and special characters
        if not any(char.isdigit() for char in passord):
            raise ValidationError('密码必须包含数字')
        if not any(char.isupper() for char in passord):
            raise ValidationError('密码必须包含大写字母')
        if not any(char.islower() for char in passord):
            raise ValidationError('密码必须包含小写字母')
        if not any(char in '!@#$%^&*()_-+,.<>:\"[]\{\}' for char in passord):
            raise ValidationError('密码必须包含特殊字符')
        if any(char in ' \t' for char in passord):
            raise ValidationError('密码不能包含空格或制表符')
        if form.username.data in passord:
            raise ValidationError('密码不能包含用户名')
        if any(char in sample_password for char in passord.lower()):
            raise ValidationError('密码不能包含常见密码')
        

class LoginForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired(), Length(min=3, max=120)],
                           render_kw={'placeholder': '请输入用户名'})
    password = PasswordField('密码', validators=[DataRequired(), Length(min=8, max=120)],
                            render_kw={'placeholder': '请输入密码'}
                            )
    remember_me = RadioField('记住我', choices=[('1', '是'), ('0', '否')], validators=[DataRequired()], default='0')
    # recaptcha = RecaptchaField()





    