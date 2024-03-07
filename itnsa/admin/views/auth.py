from flask import render_template, abort, redirect, url_for, flash, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_required, current_user

from itnsa.models import db, User, Role
from itnsa.admin import admin
from itnsa.admin.forms import ResetPasswordByAdminForm, ChangePasswordForm, UserBaseInfoEditByAdminForm, UserBaseInfoEditByUserForm, ProfileEditByAdminForm, ProfileEditByUserForm

from . import admin_required
from itnsa.common.views import generate_registration_link


# Users list view
@admin.route('/users')
@login_required
@admin_required
def users():
    if current_user.has_role('admin'):
        users = db.session.execute(db.select(User).order_by(User.id)).scalars()
        return render_template('admin/auth/users.html', users=users, title='用户列表')
    return abort(403)

# Delete user
@admin.route('/delete-user/<int:id>')
@login_required
@admin_required
def delete_user(id):
    user = db.session.execute(db.select(User).where(User.id == id)).scalar_one_or_none()
    if user:
        db.session.delete(user)
        db.session.commit()
        return redirect(url_for('admin.users'))
    return abort(404)

# User profile view and edit view
def get_roles():
    roles = db.session.execute(db.select(Role).order_by(Role.id)).scalars().all()
    return [(role.name, role.display_name) for role in roles]

@admin.route('/user/profile/<user_id>', methods=['GET', 'POST'])
@login_required
def profile(user_id):
    user = db.get_or_404(User, user_id)

    # Check permissions: admin can edit all users, user can only edit his/her own profile
    if not current_user.has_role('admin') and current_user.id != user.id:
        flash('您没有权限访问该页面', 'danger')
        return redirect(url_for('main.index'))
    
    # Display user base info form for admin and user
    # user_form.roles field get choices dynamically from the get_roles function using the `choices` attribute.
    # user_form.roles current date is the user's roles.
    if current_user.has_role('admin'):
        user_form = UserBaseInfoEditByAdminForm(obj=user)
        user_form.roles.choices = get_roles()
        if request.method == 'GET':
            user_form.roles.data = [role.name for role in user.roles]
    else:
        user_form = UserBaseInfoEditByUserForm(obj=user)
        user_form.roles.choices = [(role.name, role.display_name) for role in user.roles]
        if request.method == 'GET':
            user_form.roles.data = [role.name for role in user.roles]
    
    # Edit user base info for admin and user.

    if 'user_base_info_edit' in request.form and user_form.validate_on_submit():
        user.email = user_form.email.data
        if current_user.has_role('admin'):
            user.real_name = user_form.real_name.data
            select_roles = user_form.roles.data
            new_roles = db.session.execute(db.select(Role).filter(Role.name.in_(select_roles))).scalars().all()
            user.roles = new_roles
            user.is_active = user_form.is_active.data
        db.session.commit()
        flash('用户基本信息已更新。', 'success')
        return redirect(url_for('admin.profile', user_id=user.id))

    # Display user profile form for admin and user
    if current_user.has_role('admin'):
        profile_form = ProfileEditByAdminForm(obj=user.profile)
    else:
        profile_form = ProfileEditByUserForm(obj=user.profile)
    if 'profile_edit_submit' in request.form and profile_form.validate_on_submit():
        profile_form.populate_obj(user.profile)
        db.session.commit()
        flash('用户详细资料已更新。', 'success')
        return redirect(url_for('admin.profile', user_id=user.id))
    return render_template('admin/auth/profile.html', user_form=user_form, profile_form=profile_form, title='个人资料')

# Change user's password
@admin.route('/change-password/<int:id>', methods=['GET', 'POST'])
@login_required
def change_password(id):
    user = db.session.execute(db.select(User).where(User.id == id)).scalar_one_or_none()
    if user:
        if current_user.has_role('admin'):
            form = ResetPasswordByAdminForm()
            if form.validate_on_submit():
                user.password = generate_password_hash(form.new_password.data)
                db.session.commit()
                flash('密码已修改。', 'success')
                return redirect(url_for('admin.users'))
            return render_template('admin/auth/chpasswd.html', user=user, form=form, title='修改密码')
        if current_user.id == id:
            form = ChangePasswordForm()
            if form.validate_on_submit():
                if check_password_hash(user.password, form.old_password.data):
                    user.password = generate_password_hash(form.new_password.data)
                    db.session.commit()
                    flash('密码已修改。', 'success')
                    return redirect(url_for('admin.profile', user_id=id))
                else:
                    flash('旧密码错误。', 'danger')
            return render_template('admin/auth/chpasswd.html', user=user, form=form, title='修改密码')
    return abort(403)
                
# Roles list view
@admin.route('/roles')
@login_required
@admin_required
def roles():
    if current_user.has_role('admin'):
        roles = db.session.execute(db.select(Role).order_by(Role.id)).scalars()
        return render_template('admin/auth/roles.html', roles=roles, title='角色列表')
    return abort(403)

# Gernerate registration link with token
@admin.route('/registration-link')
@login_required
@admin_required
def reg_link():
    return render_template('admin/auth/reg-link.html', title='注册链接')

@admin.route('/api/generate-registration-link')
def gen_reg_link():
    link, link_age = generate_registration_link()
    # return render_template('admin/auth/gen-reg-link.html', link=link, link_age=link_age, title='生成注册链接')
    return jsonify({'link': link, 'link_age': link_age})

