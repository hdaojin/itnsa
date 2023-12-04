from datetime import datetime
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed, FileSize
from wtforms import StringField, DateField, RadioField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length

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