from datetime import datetime
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed, FileSize
from wtforms import StringField, DateField, RadioField, SelectField, SubmitField, IntegerField, TextAreaField
from wtforms.validators import DataRequired, Length, NumberRange, Optional
from config import app_config

# DateField默认值设置为datetime.today()。这个函数只会在模块加载时计算一次，因此如果你的应用是长时间运行的，这个日期不会更新。为了确保每次加载表单时日期都是最新的，你需要将默认值设置为一个函数，这样每次调用时都会重新计算。

def today_date():
    return datetime.today()

class TrainingLogUploadForm(FlaskForm):
    module = SelectField('模块', validators=[DataRequired()]) # Dynamic choices in view function
    date = DateField('日期', validators=[DataRequired()], default=today_date, description="*特别注意: 请选择日志对应的训练日期，不是日志上传的日期")
    task = StringField('任务', validators=[DataRequired(), Length(max=30, message='任务长度不能超过30个字符')], description='任务长度不能超过30个字符')
    type = RadioField('类型', validators=[DataRequired()]) # Dynamic choices in view function
    file = FileField('上传文件', validators=[FileRequired(), 
                                        FileAllowed(app_config.ALLOWED_EXTENSIONS, f'只能上传{app_config.ALLOWED_EXTENSIONS}文件'),
                                        FileSize(max_size=app_config.MAX_CONTENT_LENGTH, message=f'文件大小不能超过{app_config.MAX_CONTENT_LENGTH/1024/1024}M')],
                                description=f"只能上传{app_config.ALLOWED_EXTENSIONS}文件，文件大小不能超过10M",
                                )
    submit = SubmitField('上传')

class TrainingLogEvaluationForm(FlaskForm):
    score = IntegerField('完成度(%)', validators=[DataRequired(), NumberRange(min=0, max=100, message='完成度必须是在0到100之间的整数')], description='完成度必须是在0到100之间的整数')
    comment = TextAreaField('评价', validators=[Optional(), Length(max=1024, message='评价长度不能超过1024个字符')], description='评价长度不能超过1024个字符')
    submit = SubmitField('提交')