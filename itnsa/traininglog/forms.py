from datetime import datetime
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed, FileSize
from wtforms import StringField, DateField, RadioField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length

# class TrainingLogModuleForm(FlaskForm):
#     name = StringField('模块名称', validators=[DataRequired(), Length(max=20, message='模块名称长度不能超过20个字符')])
#     display_name = StringField('模块显示名称', validators=[DataRequired(), Length(max=20, message='模块显示名称长度不能超过20个字符')])
#     description = StringField('模块描述', validators=[Length(max=100, message='模块描述长度不能超过100个字符')])
#     submit = SubmitField('提交')

class TrainingLogUploadForm(FlaskForm):
    module = SelectField('模块', choices=[
        ('Linux', 'Linux'), 
        ('Windows', 'Windows'),
        ('Network', 'Network'),
        ('Automation', 'Automation'),
        ('English', 'English'),
        ('Other', 'Other'),
        ], validators=[DataRequired()]) 
    date = DateField('日期', validators=[DataRequired()], default=datetime.today())
    task = StringField('任务', validators=[DataRequired(), Length(max=20, message='任务长度不能超过20个字符')])
    type = RadioField('类型', choices=[
        ('世界技能大赛网络系统管理项目训练日志', '世界技能大赛网络系统管理项目训练日志')], 
        render_kw={'placeholder': '当天训练任务'}, 
        default='世界技能大赛网络系统管理项目训练日志', 
        validators=[DataRequired()])
    file = FileField('上传文件', validators=[FileRequired(), 
                                        FileAllowed(['pdf'], '只能上传PDF文件'),
                                        FileSize(max_size=1024*1024*10, message='文件大小不能超过10M')],
                                description="只能上传PDF文件，文件大小不能超过10M",
                                )
    submit = SubmitField('上传')