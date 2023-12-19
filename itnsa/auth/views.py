from flask import  render_template, url_for, redirect, request, flash, current_app, abort
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from itnsa.models import db, User, Role, UserProfile
from itnsa.common.views import validate_registration_link

from .forms import LoginForm, RegisterForm, UserEditByAdminForm, UserEditByUserForm, ProfileEditForm
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

# User profile view and edit view
def get_roles():
    roles = db.session.execute(db.select(Role).order_by(Role.id)).scalars().all()
    return [(role.name, role.display_name) for role in roles]

@auth.route('/user/profile/<user_id>', methods=['GET', 'POST'])
@login_required
def profile(user_id):
    user = db.get_or_404(User, user_id)

    # Check permissions: admin can edit all users, user can only edit his/her own profile
    if not current_user.has_role('admin') and current_user.id != user.id:
        flash('您没有权限访问该页面', 'danger')
        return redirect(url_for('main.index'))

    if current_user.has_role('admin'):
        user_form = UserEditByAdminForm(obj=user)
        user_form.roles.choices = get_roles()
        if request.method == 'GET':
            user_form.roles.data = [role.name for role in user.roles]
    else:
        user_form = UserEditByUserForm(obj=user)
        user_form.roles.choices = [(role.name, role.display_name) for role in user.roles]
        if request.method == 'GET':
            user_form.roles.data = [role.name for role in user.roles]

    profile_form = ProfileEditForm(obj=user.profile)

    if 'user_edit_submit' in request.form and user_form.validate_on_submit():
        user.email = user_form.email.data
        if current_user.has_role('admin'):
            user.username = user_form.username.data
            user.real_name = user_form.real_name.data
            selected_roles = user_form.roles.data
            new_roles = db.session.execute(db.select(Role).filter(Role.name.in_(selected_roles))).scalars().all()
            user.roles = new_roles
            user.is_active = user_form.is_active.data
        db.session.commit()
        flash('用户基本信息已更新。', 'success')
        return redirect(url_for('auth.profile', user_id=user.id))

    if 'profile_edit_submit' in request.form and profile_form.validate_on_submit():
        profile_form.populate_obj(user.profile)
        db.session.commit()
        flash('用户详细资料已更新。', 'success')
        return redirect(url_for('auth.profile', user_id=user.id))
    return render_template('auth/profile.html', user_form=user_form, profile_form=profile_form, title='个人资料')





