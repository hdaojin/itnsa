from typing import Any
from flask_wtf import FlaskForm
from wtforms import StringField, RadioField, PasswordField, SubmitField, BooleanField, SelectField, SelectMultipleField, HiddenField, DateField, TextAreaField, TelField, EmailField
from wtforms.validators import DataRequired, InputRequired, Length, EqualTo, Email, ValidationError, ReadOnly, Disabled, Optional

from datetime import datetime

# from ..models import db, User, Role



class RegisterForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired(), Length(min=3, max=120)], description="用户名长度不能少于3个字符, 且只能包含字母、数字、短横杠和下划线",
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
    submit = SubmitField('登录')

class UserEditByAdminForm(RegisterForm):
    roles = SelectMultipleField('角色', validators=[DataRequired()])  # Dynamic choices in view function
    password = HiddenField('密码',  render_kw={'disabled': True})
    confirm = HiddenField('确认密码', render_kw={'disabled': True})
    is_active = BooleanField('激活') # InputRequired() 验证器会验证用户是否勾选了复选框，可以允许用户不勾选复选框，为False
    submit = SubmitField('保存', name='user_edit_submit')


class UserEditByUserForm(UserEditByAdminForm):
    username = StringField('用户名', render_kw={'disabled': True})
    real_name = StringField('真实姓名', render_kw={'disabled': True})
    roles = SelectMultipleField('角色', render_kw={'disabled': True})  # Dynamic choices in view function
    is_active = BooleanField('激活', render_kw={'disabled': True})

student_state_choices = [
    ('在读', '在读'),
    ('退班', '退班'),
    ('毕业', '毕业'),
    ('留校', '留校'),
    ('其他', '其他')
]

class ProfileEditForm(FlaskForm):
    student_id = StringField('学号', validators=[Optional(), Length(min=2, max=18, message='字段长度必须介于 2 到 18 个字符之间。')])
    gender = RadioField('性别', choices=[('男', '男'), ('女', '女')], validators=[Optional()])
    id_card = StringField('身份证号', validators=[Optional(), Length(min=18, max=18, message='字段长度必须为 18 个字符。')])
    birthday = DateField('出生日期', validators=[Optional()])
    mobile = TelField('手机号', validators=[Optional(), Length(min=11, max=11, message='字段长度必须为 11 个字符。')])
    address = StringField('家庭住址', validators=[Optional(), Length(min=2, max=120, message='字段长度必须介于 2 到 120 个字符之间。')])
    original_class = StringField('原班级', validators=[Optional(), Length(min=2, max=120, message='字段长度必须介于 2 到 120 个字符之间。')])
    original_class_manager = StringField('原班主任', validators=[Optional(), Length(min=2, max=10, message='字段长度必须介于 2 到 10 个字符之间。')])
    original_class_manager_mobile = TelField('原班主任电话', validators=[Optional(), Length(min=11, max=11, message='字段长度必须为 11 个字符。')])
    dormitory = StringField('宿舍', validators=[Optional(), Length(min=2, max=20, message='字段长度必须介于 2 到 20 个字符之间。')])
    emergency_contact = StringField('紧急联系人', validators=[Optional(), Length(min=2, max=10, message='字段长度必须介于 2 到 10 个字符之间。')])
    emergency_contact_mobile = TelField('紧急联系人电话', validators=[Optional(), Length(min=11, max=11, message='字段长度必须为 11 个字符。')])
    join_date = DateField('加入精英班日期', validators=[Optional()])
    class_student_id = StringField('精英班学号', validators=[Optional(), Length(min=2, max=18, message='字段长度必须介于 2 到 18 个字符之间。')])
    state = SelectField('状态', choices=student_state_choices, validators=[Optional()], default='在读')
    departure_date = DateField('离开精英班日期', validators=[Optional()])
    competition_results = TextAreaField('竞赛成绩', validators=[Optional(), Length(max=1024, message='字段长度不能超过1024个字符')])
    honors = TextAreaField('荣誉', validators=[Optional(), Length(max=1024, message='字段长度不能超过1024个字符')])
    submit = SubmitField('保存', name='profile_edit_submit')


    # student_id = StringField('学号', validators=[Length(min=2, max=18)])
    # gender = RadioField('性别', choices=[('男', '男'), ('女', '女')], validators=[DataRequired()])
    # id_card = StringField('身份证号', validators=[Length(min=18, max=18)])
    # birthday = DateField('出生日期', default=datetime.now())
    # # mobile = StringField('手机号', validators=[Length(min=11, max=11)])
    # mobile = TelField('手机号', validators=[Length(min=11, max=11)])
    # address = StringField('家庭住址', validators=[Length(min=2, max=120)])
    # original_class = StringField('原班级', validators=[Length(min=2, max=120)])
    # original_class_manager = StringField('原班主任', validators=[Length(min=2, max=120)])
    # dormitory = StringField('宿舍', validators=[Length(min=2, max=120)])
    # emergency_contact = StringField('紧急联系人', validators=[Length(min=2, max=120)])
    # emergency_contact_mobile = StringField('紧急联系人电话', validators=[Length(min=11, max=11)])
    # join_date = DateField('加入精英班日期', default=datetime.now())
    # class_student_id = StringField('精英班学号', validators=[Length(min=2, max=18)])
    # state = SelectField('状态', choices=student_state_choices, default='在读')
    # departure_date = DateField('离开精英班日期', default=datetime.now())
    # competition_results = TextAreaField('竞赛成绩')
    # honors = TextAreaField('荣誉')
    # submit = SubmitField('保存', name='profile_edit_submit')

