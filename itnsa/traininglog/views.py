from flask import render_template, request, url_for, redirect, flash, send_from_directory, current_app, abort
# from werkzeug.utils import secure_filename

from pathlib import Path
from datetime import datetime, timedelta
from functools import wraps

from flask_login import login_required, current_user
from sqlalchemy import union_all

from itnsa.traininglog.forms import TrainingLogUploadForm, TrainingLogEvaluationForm
from itnsa.models import db, User, Role, TrainingLog, TrainingModule, TrainingType, TrainingLogEvaluation
from itnsa.traininglog import traininglog

upload_folder = Path(current_app.config['UPLOAD_FOLDER'])

# upload training log using flask-wtf form to UPLOAD_FOLDER and save filename to database

def get_training_modules():
    training_modules = db.session.execute(db.select(TrainingModule).order_by(TrainingModule.id)).scalars().all()
    return [(training_module.name, training_module.display_name) for training_module in training_modules]

def get_training_types():
    training_types = db.session.execute(db.select(TrainingType).order_by(TrainingType.id)).scalars().all()
    return [(training_type.name, training_type.display_name) for training_type in training_types]

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
    form.module.choices = get_training_modules()
    form.type.choices = get_training_types()
    if request.method == 'GET':
        #form.type.default = 'WorldSkillsItnsaEliteClass'
        form.type.default = 'WorldSkillsItnsaChinaTeam'
        form.process()

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
        
        training_module = db.session.execute(db.select(TrainingModule).where(TrainingModule.name==module)).scalar_one()
        training_type = db.session.execute(db.select(TrainingType).where(TrainingType.name==type)).scalar_one()
        complate_training_type_display_name = training_type.display_name + '训练日志'

        filename = "-".join([complate_training_type_display_name, role, date.strftime('%Y.%m.%d'), name, training_module.display_name, task.replace(' ', '-')]) + '.' + file.filename.rsplit('.', 1)[1].lower()

        training_log = TrainingLog(
            module_id=training_module.id,
            date=date,
            task=task,
            type_id=training_type.id,
            file=filename,
            user_id=user_id,
            role=role
        )
        db.session.add(training_log)
        db.session.commit()

        # Create a training log evaluation instance
        evaluation = TrainingLogEvaluation(training_log_id=training_log.id)
        db.session.add(evaluation)
        db.session.commit()

        # filename = secure_filename(file.filename)
        # current_month = datetime.now().strftime('%Y-%m')
        file_year = date.strftime('%Y')
        file_month = date.strftime('%m')
        upload_folder_path = upload_folder.joinpath(file_year, file_month)
        
        # Create upload folder if it doesn't exist
        upload_folder_path.mkdir(parents=True, exist_ok=True)

        file.save(upload_folder_path.joinpath(filename))
        flash('上传成功', 'success')
        return redirect(url_for('traininglog.list_training_logs'))
    else:
        print(form.errors)
    
    return render_template('traininglog/upload.html', title='上传训练日志', form = form)

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
    end_date = datetime(year + 1, 1, 1) if month == 12 else datetime(year, month + 1, 1)

    # if day is specified, get a day
    if day:
        start_date = datetime(year, month, day)
        end_date = start_date + timedelta(days=1)

    # select logics
    
    query = db.select(TrainingLog).where(TrainingLog.date >= start_date, TrainingLog.date < end_date)

    # Display all training logs if user is admin
    if current_user.has_role('admin'):
        training_logs = db.session.execute(query.order_by(TrainingLog.date)).scalars()
    else:
        # Get IDs of all coaches and competitors
        coaches_ids = db.session.execute(db.select(User.id).join(User.roles).where(Role.name=='coach')).scalars().all()
        competitors_ids = db.session.execute(db.select(User.id).join(User.roles).where(Role.name=='competitor')).scalars().all()
        # If current user if a coach who can view all training logs of competitors and himself
        if current_user.has_role('coach') and not current_user.has_role('admin'):
            allowed_ids = [current_user.id] + competitors_ids
        # If current user if a competitor who can view all training logs of coaches and himself
        elif current_user.has_role('competitor'):
            allowed_ids = [current_user.id] + coaches_ids
        else:
            allowed_ids = [current_user.id]
        
        training_logs = db.session.execute(query.where(TrainingLog.user_id.in_(allowed_ids)).order_by(TrainingLog.date)).scalars()

    end_date = end_date - timedelta(days=1)
    title = f"{start_date.strftime('%Y.%m.%d')} - {end_date.strftime('%Y.%m.%d')} 训练日志列表"

    return render_template('traininglog/list.html', title=title, training_logs=training_logs, year=year, month=month, day=day)

# view training log and evaluation
@traininglog.route('/view/<path:filename>')
def uploaded_file(filename):
    """ list all training logs"""
    return send_from_directory(upload_folder, filename)

@traininglog.route('/view/<int:id>', methods=['GET', 'POST'])
@login_required
def view_training_log(id):
    """ view training log"""
    training_log = db.session.execute(db.select(TrainingLog).where(TrainingLog.id == id)).scalar_one()
    # Competitor can view his/her own training log and coach's training log;
    # Coach can view his/her own training log and competitor's training log;
    # Admin can view all training logs
    if current_user.has_role('admin'):
        pass
    elif current_user.has_role('coach'):
        if training_log.user_id != current_user.id and not any(role.name == 'competitor' for role in training_log.user.roles):
            abort(403)
    elif current_user.has_role('competitor'):
        if training_log.user_id != current_user.id and not any(role.name == 'coach' for role in training_log.user.roles):
            abort(403)
    else:
        abort(403)

    form = TrainingLogEvaluationForm()

    if form.validate_on_submit() and current_user.has_role('coach'):
        if not training_log.evaluation:
            training_log.evaluation = TrainingLogEvaluation()

        training_log.evaluation.score = form.score.data
        training_log.evaluation.comment = form.comment.data
        training_log.evaluation.user_id = current_user.id
        training_log.evaluation.training_log_id = id
        db.session.commit()
        flash('评价已更新', 'success')
        return redirect(url_for('traininglog.view_training_log', id=id))
    
    if training_log.evaluation:
        form.score.data = training_log.evaluation.score
        form.comment.data = training_log.evaluation.comment

    return render_template('traininglog/view.html', title='训练日志', training_log=training_log, form=form)


# Delete training log from database and file system
# Delete training log from database
@traininglog.route('/delete/<int:id>')
@login_required
def delete_training_log(id):
    """ delete training log"""
    training_log = db.get_or_404(TrainingLog, id)
    # User can only delete his/her own training log except admin
    if not current_user.has_role('admin'):
        if training_log.user_id != current_user.id:
            abort(403)

    taining_log_path = upload_folder.joinpath(training_log.date.strftime('%Y'), training_log.date.strftime('%m'), training_log.file)
    if taining_log_path.exists():
        taining_log_path.unlink()
    db.session.delete(training_log)
    db.session.commit()
    flash('删除成功', 'success')
    return redirect(url_for('traininglog.list_training_logs'))
