from datetime import datetime
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed, FileSize
from wtforms import StringField, DateField, RadioField, SelectField, SubmitField, IntegerField, TextAreaField
from wtforms.validators import DataRequired, Length, NumberRange, Optional

class TrainingLogUploadForm(FlaskForm):
    module = SelectField('模块', validators=[DataRequired()]) # Dynamic choices in view function
    date = DateField('日期', validators=[DataRequired()], default=datetime.today())
    task = StringField('任务', validators=[DataRequired(), Length(max=20, message='任务长度不能超过20个字符')])
    type = RadioField('类型', validators=[DataRequired()]) # Dynamic choices in view function
    file = FileField('上传文件', validators=[FileRequired(), 
                                        FileAllowed(['pdf'], '只能上传PDF文件'),
                                        FileSize(max_size=1024*1024*10, message='文件大小不能超过10M')],
                                description="只能上传PDF文件，文件大小不能超过10M",
                                )
    submit = SubmitField('上传')

class TrainingLogEvaluationForm(FlaskForm):
    score = IntegerField('完成度(%)', validators=[DataRequired(), NumberRange(min=0, max=100, message='完成度必须是在0到100之间的整数')], description='完成度必须是在0到100之间的整数')
    comment = TextAreaField('评价', validators=[Optional(), Length(max=1024, message='评价长度不能超过1024个字符')], description='评价长度不能超过1024个字符')
    submit = SubmitField('提交')