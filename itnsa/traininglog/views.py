from flask import render_template, request, url_for, redirect, flash, send_from_directory, current_app
# from werkzeug.utils import secure_filename

from pathlib import Path
from datetime import datetime, timedelta

from flask_login import login_required, current_user
from sqlalchemy import union

from .forms import TrainingLogUploadForm, TrainingLogModuleForm, TrainingLogTypeForm
from ..models import db, Users,  Roles, TrainingLogs, TrainingLogModules, TrainingLogTypes
from . import traininglog

upload_folder = Path(current_app.config['UPLOAD_FOLDER'])

# Add training log module to database
@traininglog.route('/module/add', methods=['GET', 'POST'])
@login_required
def add_traininglog_module():
    if current_user.has_role('admin'):
        form = TrainingLogModuleForm()
        if form.validate_on_submit():
            traininglog_module = TrainingLogModules(
                name=form.name.data,
                display_name=form.display_name.data,
                description=form.description.data
            )
            db.session.add(traininglog_module)
            db.session.commit()
            flash('模块添加成功。', 'success')
            return redirect(url_for('traininglog.add_traininglog_module'))
        



# upload training log using flask-wtf form to UPLOAD_FOLDER and save filename to database

def get_special_role_display_name():
    # 检查用户是否拥有'coach'或'competitor'角色，如果有，则返回该角色的display_name，否则返回None
    for role in current_user.roles:
        if role.name in ['coach', 'competitor']:
            return role.display_name
    return None

@traininglog.route('/upload', methods=['GET', 'POST'])
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
        if not role:
            flash('您没有权限。', 'danger')
            return redirect(url_for('traininglog.upload_training_log'))

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
        return redirect(url_for('traininglog.list_training_logs'))
    return render_template('form.html', title='上传训练日志', form = form)

# 显示当前用户可以查看的训练日志，默认显示当前月的训练日志，可通过参数指定月份；如果用户是管理员，则显示所有用户的训练日志，如果用户是教练，则显示自己和学员的训练日志，如果用户是学员，则显示自己和教练的训练日志。默认以date降序排列。
@traininglog.route('/list/')
@traininglog.route('/list/<int:year>/<int:month>/')
@traininglog.route('/list/<int:year>/<int:month>/<int:day>/')
@login_required
def list_training_logs(year=None, month=None, day=None):
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
    
    current_user_training_logs = db.session.execute(db.select(TrainingLogs).where(TrainingLogs.date >= start_date, TrainingLogs.date < end_date, TrainingLogs.user_id==current_user.id))

    if current_user.has_role('admin'):
        training_logs = db.session.execute(db.select(TrainingLogs).where(TrainingLogs.date >= start_date, TrainingLogs.date < end_date).order_by(TrainingLogs.date)).scalars()
    elif current_user.has_role('coach') and not current_user.has_role('admin'):
        competitors_training_logs = db.session.execute(db.select(TrainingLogs).where(TrainingLogs.date >= start_date, TrainingLogs.date < end_date, TrainingLogs.role=='competitor'))
        training_logs = db.session.execute(db.union_all(current_user_training_logs, competitors_training_logs)).scalars()
    elif current_user.has_role('competitor'):
        training_logs = db.session.execute(db.select(TrainingLogs).where(TrainingLogs.date >= start_date, TrainingLogs.date < end_date, TrainingLogs.user_id==current_user.id)).scalars()
    #     coach_training_logs = db.session.execute(db.select(TrainingLogs).where(TrainingLogs.date >= start_date, TrainingLogs.date < end_date, TrainingLogs.role=='coach'))
    #     training_logs = db.session.execute(db.union(current_user_training_logs, coach_training_logs)).scalars()
    else:
        training_logs = []

    end_date = end_date - timedelta(days=1)
    title = start_date.strftime('%Y.%m.%d') + '-' + end_date.strftime('%Y.%m.%d') + ' 训练日志列表'

    return render_template('traininglog/traininglogs.html', title=title, training_logs=training_logs, year=year, month=month, day=day)


# Delete training log from database and file system



# @traininglog.route('/list/<role>')
# @login_required
# def list():
#     """ list all training logs from database"""

#     training_logs = db.session.execute(db.select(TrainingLogs).where(user_id=current_user.id).order_by(TrainingLogs.id)).scalars()
#     return render_template('training_log/list.html', title='训练日志列表', training_logs=training_logs)

# view training log
@traininglog.route('/view/<path:filename>')
def uploaded_file(filename):
    """ list all training logs"""
    return send_from_directory(upload_folder, filename)

@traininglog.route('/view/<int:id>')
@login_required
def view_training_log(id):
    """ view training log"""
    training_log = db.session.execute(db.select(TrainingLogs).where(TrainingLogs.id==id)).scalar_one()
    return render_template('traininglog/single-traininglog.html', title='训练日志', training_log=training_log)


