from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length

class BaseForm(FlaskForm):
    name = StringField('名称', validators=[DataRequired(), Length(max=20, message='模块名称长度不能超过20个字符')])
    display_name = StringField('显示名称', validators=[DataRequired(), Length(max=20, message='模块显示名称长度不能超过20个字符')])
    description = StringField('描述', validators=[Length(max=100, message='模块描述长度不能超过100个字符')])
    submit = SubmitField('提交')

class TrainingLogModuleForm(BaseForm):
    pass

class TrainingLogTypeForm(BaseForm):
    pass
