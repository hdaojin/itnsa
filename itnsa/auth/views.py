from flask import  render_template, url_for, redirect, request, flash, current_app, abort
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from . import auth, login_manager
from ..models import db, User, Role
from .forms import LoginForm, RegisterForm, ProfileEditByAdminForm, ProfileEditByUserForm


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
    form = RegisterForm()
    form.roles.choices = get_common_roles()
    # form.roles.default = 'competitor'
    # form.process()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            password=generate_password_hash(form.password.data),
            real_name=form.real_name.data,
            email=form.email.data,
        )
        role = db.session.execute(db.select(Role).filter_by(name=form.roles.data)).scalar_one_or_none()
        print(role)
        if role:
            user.roles.append(role)
        else:
            return abort(400)

        db.session.add(user)
        db.session.commit()
        flash('注册成功。', 'success')
        return redirect(url_for('auth.login'))
    return render_template('form.html', form=form, title='注册')

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
    return render_template('form.html', form=form, title='登录')

# User logout view
@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('注销成功。', 'success')
    return redirect(url_for('auth.login'))

# User profile view and edit view
def get_roles():
    roles = db.session.execute(db.select(Role).order_by(Role.id)).scalars().all()
    return [(role.name, role.display_name) for role in roles]

@auth.route('/user/profile/<user_id>', methods=['GET', 'POST'])
@login_required
def profile(user_id):
    user = db.get_or_404(User, user_id)
    if current_user.has_role('admin'):
        form = ProfileEditByAdminForm(obj=user)
        form.roles.choices = get_roles()
        if request.method == 'GET':
            form.roles.data = [role.name for role in user.roles]
    else:
        form = ProfileEditByUserForm(obj=user)
        form.roles.choices = [(role.name, role.display_name) for role in user.roles]
        if request.method == 'GET':
            form.roles.data = [role.name for role in user.roles]

    if form.validate_on_submit():
        user.email = form.email.data

        if current_user.has_role('admin'):
            user.username = form.username.data
            user.real_name = form.real_name.data
            selected_roles = form.roles.data
            new_roles = db.session.execute(db.select(Role).filter(Role.name.in_(selected_roles))).scalars().all()
            user.roles = new_roles
            user.is_active = form.is_active.data

        # form.populate_obj(user)
        db.session.commit()
        flash('个人资料已更新。', 'success')
        return redirect(url_for('auth.profile', user_id=user.id))
    return render_template('form.html', form=form, title='个人资料')





