from flask import render_template, request, url_for, redirect, flash, send_from_directory, current_app, abort
# from werkzeug.utils import secure_filename

from pathlib import Path
from datetime import datetime, timedelta
from functools import wraps
import calendar

from flask_login import login_required, current_user
from sqlalchemy import union_all, desc

from itnsa.traininglog.forms import TrainingLogUploadForm, TrainingLogEvaluationForm
from itnsa.models import db, User, Role, TrainingLog, TrainingModule, TrainingType, TrainingLogEvaluation
from itnsa.traininglog import traininglog

upload_folder = Path(current_app.config['UPLOAD_FOLDER']).joinpath('training_logs')
default_training_type = current_app.config['DEFAULT_TRAINING_TYPE']

# upload training log using flask-wtf form to UPLOAD_FOLDER and save filename to database

def get_training_modules():
    training_modules = db.session.execute(db.select(TrainingModule).order_by(TrainingModule.id)).scalars().all()
    return [(training_module.name, training_module.display_name) for training_module in training_modules]

def get_training_types():
    training_types = db.session.execute(db.select(TrainingType).order_by(TrainingType.id)).scalars().all()
    return [(training_type.name, training_type.display_name) for training_type in training_types]

def get_special_role_of_user():
    # 检查用户是否拥有'coach'或'competitor', 'translator'角色，如果有，则返回该角色，否则返回None
    for role in current_user.roles:
        if role.name in ['coach', 'competitor', 'translator']:
            return role
    return None

# Get user id and real_name for all users
def get_all_users():
    users = db.session.execute(db.select(User).order_by(User.id)).scalars().all()
    return [(user.id, user.real_name) for user in users]

# Get role id and display_name for all roles
def get_all_roles():
    roles = db.session.execute(db.select(Role).where(Role.name != 'admin').order_by(Role.id)).scalars().all()
    return [(role.id, role.display_name) for role in roles]

def get_month_calendar(year, month):
    # 返回指定月的日历
    cal = calendar.monthcalendar(year, month)
    return cal

@traininglog.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_training_log():
    """ Upload training log to server."""
    form = TrainingLogUploadForm()
    form.module.choices = get_training_modules()
    form.type.choices = get_training_types()
    if request.method == 'GET':
        #form.type.default = 'WorldSkillsItnsaEliteClass'
        form.type.default = default_training_type
        form.process()

    if form.validate_on_submit():
        module = form.module.data
        train_date = form.date.data
        task = form.task.data
        type = form.type.data
        file = form.file.data
        name = current_user.real_name
        user_id = current_user.id
        role = get_special_role_of_user()
        if not role:
            flash('您没有权限。', 'danger')
            return redirect(url_for('traininglog.upload_training_log'))
        
        training_module = db.session.execute(db.select(TrainingModule).where(TrainingModule.name==module)).scalar_one()
        training_type = db.session.execute(db.select(TrainingType).where(TrainingType.name==type)).scalar_one()
        complate_training_type_short_name = training_type.short_name + '训练日志'

        filename = "-".join([complate_training_type_short_name, role.short_name, name, train_date.strftime('%Y.%m.%d'), training_module.short_name, task.replace(' ', '-')]) + '.' + file.filename.rsplit('.', 1)[1].lower()

        training_log = TrainingLog(
            module_id=training_module.id,
            train_date=train_date,
            task=task,
            type_id=training_type.id,
            file=filename,
            user_id=user_id,
        )
        db.session.add(training_log)
        db.session.commit()

        # Create a training log evaluation instance
        evaluation = TrainingLogEvaluation(training_log_id=training_log.id)
        db.session.add(evaluation)
        db.session.commit()

        # filename = secure_filename(file.filename)
        # current_month = datetime.now().strftime('%Y-%m')
        file_year = train_date.strftime('%Y')
        file_month = train_date.strftime('%m')
        upload_folder_path = upload_folder.joinpath(file_year, file_month)
        
        # Create upload folder if it doesn't exist
        upload_folder_path.mkdir(parents=True, exist_ok=True)

        file.save(upload_folder_path.joinpath(filename))
        flash('上传成功', 'success')
        return redirect(url_for('traininglog.list_training_logs', user_id=user_id))
    else:
        print(form.errors)
    
    return render_template('traininglog/upload.html', title='上传训练日志', form = form)

# 显示当前用户可以查看的训练日志，默认显示当前月的训练日志，可通过参数指定其他过滤条件，如角色，用户名，月份，日期等；默认以train_date降序排列。实现权限控制和分页功能。
@traininglog.route('/list/')
@login_required
def list_training_logs():
    # 接收浏览器传递的参数, 包括用户id，角色，月份，日期
    user_id = request.args.get('user_id')
    role_id = request.args.get('role_id')
    year_month = datetime.strptime(request.args.get('month'), '%Y-%m') if request.args.get('month') else None
    year_month_day = datetime.strptime(request.args.get('date'), '%Y-%m-%d') if request.args.get('date') else None

    # 获得给定的年份和月份，如果没有则默认为当前年份和月份
    now = datetime.now()
    year = year_month.year if year_month else now.year
    month = year_month.month if year_month else now.month
    date = year_month_day.date() if year_month_day else None

    if date:
        year = date.year
        month = date.month

    today = now.day # 今天的号, 用于在模板的日历中比较和高亮显示今天的号

    # 计算上个月,这个月和下个月的年份和月份
    last_month = {'year': year - 1, 'month': 12} if month == 1 else {'year': year, 'month': month - 1}
    current_month = {'year': now.year, 'month': now.month}
    next_month = {'year': year + 1, 'month': 1} if month == 12 else {'year': year, 'month': month + 1}

    # 获取所有角色的id和display_name，所有用户的ID和real_name，以及指定月的日历，用于在模板中显示点击链接筛选相关数据
    roles = get_all_roles()
    users = get_all_users()
    cal = get_month_calendar(year, month)

    # 实现分页功能所需的参数, 从请求的查询参数获取当前页码，如果没有则默认为1；从配置文件获取每页显示的记录数        
    # page = request.args.get('page', 1, type=int)   # 默认显示第一页
    # per_page = current_app.config['ENTRYS_PER_PAGE'] # 每页显示的记录数


    # 基础查询逻辑：查询一个月内所有的训练日志，按训练日期降序排列
    start_date = datetime(year, month, 1).date()
    end_date = datetime(year, month, calendar.monthrange(year, month)[1]).date()
    base_query = db.select(TrainingLog).where(TrainingLog.train_date >= start_date, TrainingLog.train_date <= end_date)

    # 如果用户指定了user_id, role, date等参数，则根据这些参数进行过滤
    if year_month:
        query = base_query
    elif user_id:
        query = base_query.where(TrainingLog.user_id == user_id)
    elif role_id:
        query = base_query.where(TrainingLog.user.has(User.roles.any(Role.id == role_id)))
    elif date:
        query = base_query.where(TrainingLog.train_date == date)
    else:
        query = base_query

    # 权限控制逻辑：
        # 如果用户是管理员，则显示所有用户的训练日志列表；
        # 如果用户是教练，则显示自己和学员的训练日志（用于中国集训队时可以同时显示其他教练的日志列表）；
        # 如果用户是选手，则显示自己和所有教练的训练日志。
        # 如果用户是翻译，游客，则只显示自己的训练日志。

    # Display all training logs if user is admin
    if current_user.has_role('admin'):
        query = query
    else:
        # Get IDs of all coaches and competitors
        coaches_ids = db.session.execute(db.select(User.id).join(User.roles).where(Role.name=='coach')).scalars().all()
        competitors_ids = db.session.execute(db.select(User.id).join(User.roles).where(Role.name=='competitor')).scalars().all()
        
        # # If current user is a coach who can view all training logs of competitors and himself
        # if current_user.has_role('coach') and not current_user.has_role('admin'):
        #     allowed_ids = [current_user.id] + competitors_ids
        
        # If current user is a coach who can view all training logs of competitors, cocach
        if current_user.has_role('coach') and not current_user.has_role('admin'):
            allowed_ids = competitors_ids + coaches_ids
        
        # If current user is a competitor who can view all training logs of coaches and himself
        elif current_user.has_role('competitor'):
            allowed_ids = [current_user.id] + coaches_ids
        
        # If current user is a guest who can only view all training logs of himself
        else:
            allowed_ids = [current_user.id]
        
        query = query.where(TrainingLog.user_id.in_(allowed_ids))
    # 分页查询
    # training_log_pagination = db.paginate(query, page=page, per_page=per_page, error_out=False)
    # if training_log_pagination:
    #     training_logs = training_log_pagination.items
    # else:
    #     abort(404)
    training_logs = db.session.execute(query.order_by(desc(TrainingLog.train_date)).order_by(desc(TrainingLog.uploaded_on))).scalars().all()

    # Dynamically generate title based the filter arguments, if no filter arguments, then use the a month's title
    if user_id:
        user_real_name = db.session.execute(db.select(User.real_name).where(User.id == int(user_id))).scalar_one()
        title_prefix = f"{user_real_name} {now.year}年{now.month}月的"
    elif role_id:
        role_display_name = db.session.execute(db.select(Role.display_name).where(Role.id == role_id)).scalar_one()
        title_prefix = f"{role_display_name} {now.year}年{now.month}月的"
    elif date:
        if date == datetime.now().date():
            title_prefix = "今天的"
        elif date == datetime.now().date() - timedelta(days=1):
            title_prefix = "昨天的"
        else:
            title_prefix = f"{date.strftime('%Y-%m-%d')}的"
    else:
        title_prefix = f"{year}年{month}月的"

    title = title_prefix + "训练日志列表"

    return render_template('traininglog/list.html', 
                            title=title, 
                            # training_log_pagination=training_log_pagination, 
                            training_logs=training_logs, 
                            year=year, 
                            month=month, 
                            last_month=last_month, 
                            current_month=current_month,
                            next_month=next_month, 
                            cal=cal, today=today, 
                            users=users,
                            roles=roles
                           )

# view training log and evaluation
@traininglog.route('/view/<path:filename>')
@login_required
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
        # pass
    elif current_user.has_role('competitor'):
        if training_log.user_id != current_user.id and not any(role.name == 'coach' for role in training_log.user.roles):
            abort(403)
    elif current_user.has_role('translator'):
        if training_log.user_id != current_user.id:
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

    taining_log_path = upload_folder.joinpath(training_log.train_date.strftime('%Y'), training_log.train_date.strftime('%m'), training_log.file)
    if taining_log_path.exists():
        taining_log_path.unlink()
    db.session.delete(training_log)
    db.session.commit()
    flash('删除成功', 'success')
    return redirect(url_for('traininglog.list_training_logs', month=training_log.train_date.strftime('%Y-%m')))


# 日志提交情况统计功能

@traininglog.route('/stats')
@login_required
def log_stats():
    now = datetime.now()
    year = request.args.get('year', default=now.year, type=int)
    month = request.args.get('month', default=now.month, type=int)

    first_day = datetime(year, month, 1).date()

    # 如果是当前月份，则last_day为今天的日期
    if year == now.year and month == now.month:
        last_day = now.date()
    else:
        last_day = datetime(year, month, calendar.monthrange(year, month)[1]).date()

    training_logs = db.session.execute(db.select(TrainingLog).where(TrainingLog.train_date.between(first_day, last_day))).scalars().all()

    # 初始化每天的统计数据
    daily_stats = {day: {'coach': [], 'competitor_submitted': [], 'competitor_not_submitted': []} for day in range(1, last_day.day + 1)}
    # daily_stats = { date: {'coach': [], 'competitor_submitted': [], 'competitor_not_submitted': []} for date in [datetime(year, month, day).date() for day in range(1, last_day.day + 1)]}

    # 标记出一个月中所有的周日
    sundays = [day for day in range(1, last_day.day + 1) if datetime(year, month, day).weekday() == 6]


    # 预先查询所有的选手
    competitors_query = db.select(User).join(User.roles).where(Role.name == "competitor")
    all_competitors = set(db.session.execute(competitors_query).scalars().all())

    submitted_competitors_per_day = {day: set() for day in range(1, last_day.day + 1)}

    for traininglog in training_logs:
        day = traininglog.train_date.day
        if traininglog.user.has_role('coach') or traininglog.user.has_role('translator'):
            daily_stats[day]['coach'].append(traininglog.user.real_name)
        elif traininglog.user.has_role('competitor'):
            daily_stats[day]['competitor_submitted'].append(traininglog.user.real_name)
            submitted_competitors_per_day[day].add(traininglog.user)

    # 计算未提交日志的选手
    for day in range(1, last_day.day + 1):
        submitted_competitors = submitted_competitors_per_day[day]
        not_submitted_competitors = all_competitors - submitted_competitors
        daily_stats[day]['competitor_not_submitted'] = [competitor.real_name for competitor in not_submitted_competitors]

    coachs_traininglogs_count = sum(len(logs['coach']) for logs in daily_stats.values())
    competitors_traininglogs_count = sum(len(logs['competitor_submitted']) for logs in daily_stats.values())

    counts = {
        'coachs_traininglogs_count': coachs_traininglogs_count,
        'competitors_traininglogs_count': competitors_traininglogs_count,
    }

    return render_template('traininglog/stats.html', title='训练日志提交情况统计', daily_stats=daily_stats, now=now, year=year, month=month, sundays=sundays, counts=counts)