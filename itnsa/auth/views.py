from flask import  render_template, url_for, redirect, request, flash, current_app, abort
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

import re

from itnsa.models import db, User, Role, UserProfile
from itnsa.common.views import validate_registration_link

from .forms import LoginForm, RegisterForm
from . import auth, login_manager


# flask-login extension register a callback function that loads a user from the database. 
@login_manager.user_loader
def load_user(user_id):
    return db.session.execute(db.select(User).filter_by(id=user_id)).scalar_one_or_none()

# User register view

# The `get_roles` function is used to dynamically generate choices for the `role` field in the `RegisterForm` form. roles except 'admin' are available for registration.
def get_common_roles():
    roles = db.session.execute(db.select(Role).filter(Role.name != 'admin').order_by(Role.id)).scalars().all()
    return [(role.name, role.display_name) for role in roles]

@auth.route('/register', methods=['GET', 'POST'])
def register():
    token = request.args.get('token') # get token from url
    if not validate_registration_link(token): # validate token
        flash('注册链接无效或已过期。', 'danger')
        return redirect(url_for('main.index'))

    form = RegisterForm()
    form.roles.choices = get_common_roles()
    if request.method == 'GET':
        form.roles.default = 'competitor'
        form.process()
        
    if form.validate_on_submit():
        username = form.username.data
        if not re.match(r'^[a-zA-Z0-9_-]{3,120}$', username):
            flash('用户名只能包含字母、数字、短横杠和下划线。', 'danger')
            return redirect(url_for('auth.register'))
        
        user = db.session.execute(db.select(User).filter_by(username=form.username.data)).scalar_one_or_none()
        if user:
            flash('用户名已存在。', 'danger')
            return redirect(url_for('auth.register'))
        
        user = User(
            username=form.username.data,
            password=generate_password_hash(form.password.data),
            real_name=form.real_name.data,
            email=form.email.data,
        )
        role = db.session.execute(db.select(Role).filter_by(name=form.roles.data)).scalar_one_or_none()
        if role:
            user.roles.append(role)
        else:
            return abort(400)

        db.session.add(user)
        db.session.commit()

        # Create a user profile instance
        profile = UserProfile(user_id=user.id)
        db.session.add(profile)
        db.session.commit()

        flash('注册成功。', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form, title='注册')

# User login view
@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user_obj = db.session.execute(db.select(User).filter_by(username=form.username.data)).scalar_one_or_none()
        if user_obj and not user_obj.is_active:
            flash('用户未激活。', 'danger')
            return redirect(url_for('auth.login'))
        if user_obj and check_password_hash(user_obj.password, form.password.data):
            login_user(user_obj, remember=form.remember_me.data)
            flash('登录成功。', 'success')
            return redirect(request.args.get('next') or url_for('main.index'))
        flash('用户名或密码错误。', 'danger')
    return render_template('auth/login.html', form=form, title='登录')

# User logout view
@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('注销成功。', 'success')
    return redirect(url_for('auth.login'))


