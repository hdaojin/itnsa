from flask import  render_template, url_for, redirect, request, flash, current_app, abort, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from . import auth, login_manager
from ..models import db, Users, Roles
from .forms import LoginForm, RegisterForm


# flask-login extension register a callback function that loads a user from the database. 
@login_manager.user_loader
def load_user(user_id):
    return db.session.execute(db.select(Users).filter_by(id=user_id)).scalar_one_or_none()

# User register view
@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user = Users(
            username=form.username.data,
            password=generate_password_hash(form.password.data),
            real_name=form.real_name.data,
            email=form.email.data,
        )
        role = db.session.execute(db.select(Roles).filter_by(name=form.role.data)).scalar_one_or_none()
        if role:
            user.roles.append(role)
        else:
            return abort(400)

        db.session.add(user)
        db.session.commit()
        flash('注册成功。', 'success')
        return redirect(url_for('auth.login'))
    return render_template('form.html', form=form, title='注册')

# User activate by administator view
@auth.route('/activate/<user_id>')
@login_required
def activate(user_id):
    if current_user.has_role('admin'):
        user = db.session.execute(db.select(Users).filter_by(id=user_id)).scalar_one_or_none()
        if user:
            user.is_active = True
            db.session.commit()
            flash('用户已激活。', 'success')
        else:
            flash('用户不存在。', 'danger')
    else:
        flash('没有权限。', 'danger')
    return redirect(url_for('auth.users'))

# User deactivate by administator view
@auth.route('/deactivate/<user_id>')
@login_required
def deactivate(user_id):
    if current_user.has_role('admin'):
        user = db.session.execute(db.select(Users).filter_by(id=user_id)).scalar_one_or_none()
        if user:
            user.is_active = False
            db.session.commit()
            flash('用户已停用。', 'success')
        else:
            flash('用户不存在。', 'danger')
    else:
        flash('没有权限。', 'danger')
    return redirect(url_for('auth.users'))


# User login view
@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user_obj = db.session.execute(db.select(Users).filter_by(username=form.username.data)).scalar_one_or_none()
        if user_obj and not user_obj.is_active:
            flash('用户未激活。', 'danger')
            return redirect(url_for('auth.login'))
        if user_obj and check_password_hash(user_obj.password, form.password.data):
            login_user(user_obj, remember=form.remember_me.data)
            flash('登录成功。', 'success')
            return redirect(request.args.get('next') or url_for('main.index'))
        flash('用户名或密码错误。', 'danger')
    return render_template('form.html', form=form, title='登录')

# User logout view
@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('注销成功。', 'success')
    return redirect(url_for('auth.login'))

# Users list view
@auth.route('/users')
@login_required
def users():
    users = db.session.execute(db.select(Users).order_by(Users.id)).scalars()
    return render_template('auth/users.html', users=users, title='用户列表')


# User profile view
@auth.route('/profile/<user_id>')
@login_required
def profile(user_id):
    user = db.session.execute(db.select(Users).filter_by(id=user_id)).scalar_one_or_none()
    if not user:
        abort(404)
    return render_template('auth/profile.html', title='个人资料')

# @current_app.context_processor
def inject_auth_nav():
    register = {'name': '注册', 'url': url_for('auth.register')}
    login = {'name': '登录', 'url': url_for('auth.login')}
    logout = {'name': '注销', 'url': url_for('auth.logout')}
    return dict(register=register, login=login, logout=logout)


