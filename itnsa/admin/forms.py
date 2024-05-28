from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, SelectField, SelectMultipleField, BooleanField, RadioField, TextAreaField, DateField, HiddenField, EmailField, TelField
from wtforms.validators import DataRequired, Length, Optional

# Training log module and type form
class BaseForm(FlaskForm):
    name = StringField('名称', validators=[DataRequired(), Length(max=30, message='模块名称长度不能超过30个字符')])
    display_name = StringField('显示名称', validators=[DataRequired(), Length(max=30, message='模块显示名称长度不能超过30个字符')])
    short_name = StringField('简称', validators=[DataRequired(), Length(max=10, message='模块简称长度不能超过10个字符')])
    description = StringField('描述', validators=[Length(max=100, message='模块描述长度不能超过100个字符')])
    submit = SubmitField('提交')

class TrainingLogModuleForm(BaseForm):
    pass

class TrainingLogTypeForm(BaseForm):
    pass

# user base info form
class UserBaseInfoForm(FlaskForm):
    username = StringField('用户名',  render_kw={'disabled': True})
    real_name = StringField('真实姓名', render_kw={'disabled': True})
    roles = SelectMultipleField('角色', render_kw={'disabled': True})  # Dynamic choices in view function
    email = EmailField('邮箱', validators=[DataRequired(), Length(min=5, max=64)])
    is_active = BooleanField('激活', render_kw={'disabled': True})
    submit = SubmitField('保存', name='user_base_info_edit')

# Edit user base info form for user
class UserBaseInfoEditByUserForm(UserBaseInfoForm):
    pass

# Edit user base info form for admin
class UserBaseInfoEditByAdminForm(UserBaseInfoForm):
    real_name = StringField('真实姓名', validators=[DataRequired(), Length(min=2, max=120, message='用户名长度必须介于 2 到 120 个字符之间。')])
    roles = SelectMultipleField('角色', validators=[DataRequired()])  # Dynamic choices in view function
    is_active = BooleanField('激活') # InputRequired() 验证器会验证用户是否勾选了复选框，可以允许用户不勾选复选框，为False

# Change user profile Form
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
    # submit = SubmitField('锁定', name='profile_edit_lock')

# Change user profile Form for user
class ProfileEditByUserForm(ProfileEditForm):
    state = SelectField('状态', choices=student_state_choices, validators=[Optional()], render_kw={'disabled': True})
    departure_date = DateField('离开精英班日期', validators=[Optional()], render_kw={'disabled': True})
    competition_results = TextAreaField('竞赛成绩', validators=[Optional(), Length(max=1024, message='字段长度不能超过1024个字符')], render_kw={'disabled': True})
    honors = TextAreaField('荣誉', validators=[Optional(), Length(max=1024, message='字段长度不能超过1024个字符')], render_kw={'disabled': True})


# Change user profile Form for admin
class ProfileEditByAdminForm(ProfileEditForm):
    pass
    # submit = SubmitField('解锁', name='profile_edit_unlock')


# Change password form for admin and user
class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('旧密码', validators=[DataRequired(), Length(min=8, max=20, message='密码长度必须在8到20个字符之间')], render_kw={'placeholder': '请输入旧密码'})
    new_password = PasswordField('新密码', validators=[DataRequired(), Length(min=8, max=20, message='密码长度必须在8到20个字符之间')], render_kw={'placeholder': '请输入新密码'})
    confirm = PasswordField('确认密码', validators=[DataRequired(), Length(min=8, max=20, message='密码长度必须在8到20个字符之间')], render_kw={'placeholder': '请再次输入新密码'})
    submit = SubmitField('提交')

class ResetPasswordByAdminForm(ChangePasswordForm):
    old_password = None


