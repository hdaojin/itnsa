from flask import render_template, abort, redirect, url_for
from flask_login import login_required, current_user

from itnsa.models import db, User, Role
from itnsa.admin import admin
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
@admin.route('/gernerate-registration-link')
@login_required
@admin_required
def gen_reg_link():
    link = generate_registration_link()
    return render_template('admin/auth/gen-reg-link.html', link=link, title='生成注册链接')

