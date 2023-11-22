from flask import render_template, request, url_for, redirect, flash, send_from_directory, current_app
# from werkzeug.utils import secure_filename

from pathlib import Path
from datetime import datetime, timedelta

from sqlalchemy import select
from flask_login import login_required, current_user

from .forms import TrainingLogUploadForm
from ..models import db, Users,  Roles, TrainingLogs
from . import upload

upload_folder = Path(current_app.config['UPLOAD_FOLDER'])

# upload training log using flask-wtf form to UPLOAD_FOLDER and save filename to database

def get_special_role_display_name():
    # 检查用户是否拥有'coach'或'competitor'角色，如果有，则返回该角色的display_name，否则返回None
    for role in current_user.roles:
        if role.name in ['coach', 'competitor']:
            return role.display_name
    return None

@upload.route('/training-log', methods=['GET', 'POST'])
@login_required
def upload_training_log():
    """ Upload training log to server."""
    form = TrainingLogUploadForm()
    if form.validate_on_submit():
        module = form.module.data
        date = form.date.data
        task = form.task.data
        type = form.type.data
        file = form.file.data
        name = current_user.real_name
        user_id = current_user.id
        role = get_special_role_display_name()

        filename = "-".join([type, role, date.strftime('%Y.%m.%d'), name, module, task.replace(' ', '-')]) + '.' + file.filename.rsplit('.', 1)[1].lower()

        training_log = TrainingLogs(
            module=module,
            date=date,
            task=task,
            type=type,
            file=filename,
            user_id=user_id,
            role=role
        )
        db.session.add(training_log)
        db.session.commit()
        

        # filename = secure_filename(file.filename)
        # current_month = datetime.now().strftime('%Y-%m')
        file_year = date.strftime('%Y')
        file_month = date.strftime('%m')
        upload_folder_path = upload_folder.joinpath(file_year, file_month)
        
        # Create upload folder if it doesn't exist
        upload_folder_path.mkdir(parents=True, exist_ok=True)

        file.save(upload_folder_path.joinpath(filename))
        flash('上传成功')
        return redirect(url_for('training_log.list'))
    return render_template('form.html', title='上传训练日志', form = form)

# 显示当前用户可以查看的训练日志，默认显示当前月的训练日志，可通过参数指定月份；如果用户是管理员，则显示所有用户的训练日志，如果用户是教练，则显示自己和学员的训练日志，如果用户是学员，则显示自己和教练的训练日志。默认以date降序排列。
@upload.route('/list')
@upload.route('/list/<int:year>/<int:month>/')
@upload.route('/list/<int:year>/<int:month>/<int:day>/')
@login_required
def list(year=None, month=None, day=None):
    if not year or not month:
        year = datetime.now().year
        month = datetime.now().month

    # get a month
    start_date = datetime(year, month, 1)
    if month == 12:
        end_date = datetime(year+1, 1, 1)
    else:
        end_date = datetime(year, month+1, 1)

    # if day is specified, get a day
    if day:
        start_date = datetime(year, month, day)
        end_date = start_date + timedelta(days=1)

    # select logics
    if current_user.has_role('admin'):
        training_logs = db.session.execute(db.select(TrainingLogs).filter(TrainingLogs.date >= start_date, TrainingLogs.date < end_date).order_by(TrainingLogs.date)).scalars()
    elif current_user.has_role('coach') and not current_user.has_role('admin'):
        training_logs = select(TrainingLogs).where(TrainingLogs.date >= start_date, TrainingLogs.date < end_date).order_by(TrainingLogs.date)
        
        # competitors = db.session.execute(db.select(UserRoles).join(Role).filter(Role.name=='competitor')).scalars()
        # training_logs = db.session.execute(db.select(TrainingLogs).filter(TrainingLogs.date >= start_date, TrainingLogs.date < end_date, TrainingLogs.user_id.in_([current_user.id]))).scalars()

    # elif current_user.has_role('competitor'):
    #     training_logs = db.session.execute(db.select(TrainingLogs).filter_by(TrainingLogs.date >= start_date, TrainingLogs.date < end_date, TrainingLogs.user_id.in_([current_user.id, current_user.coach_id]))).scalars()
    else:
        training_logs = []

    return render_template('training_log/list.html', title='训练日志列表', training_logs=training_logs, year=year, month=month, day=day)





# @upload.route('/list/<role>')
# @login_required
# def list():
#     """ list all training logs from database"""

#     training_logs = db.session.execute(db.select(TrainingLogs).filter_by(user_id=current_user.id).order_by(TrainingLogs.id)).scalars()
#     return render_template('training_log/list.html', title='训练日志列表', training_logs=training_logs)

@upload.route('/veiw/<path:filename>')
def uploaded_file(filename):
    """ list all training logs"""
    return send_from_directory(upload_folder, filename)