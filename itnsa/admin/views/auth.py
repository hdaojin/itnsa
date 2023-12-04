from flask import render_template, abort
from flask_login import login_required, current_user
from itnsa.models import db, User, Role
from itnsa.admin import admin

# Users list view
@admin.route('/users')
@login_required
def users():
    if current_user.has_role('admin'):
        users = db.session.execute(db.select(User).order_by(User.id)).scalars()
        return render_template('admin/auth/users.html', users=users, title='用户列表')
    return abort(403)

# Roles list view
@admin.route('/roles')
@login_required
def roles():
    if current_user.has_role('admin'):
        roles = db.session.execute(db.select(Role).order_by(Role.id)).scalars()
        return render_template('admin/auth/roles.html', roles=roles, title='角色列表')
    return abort(403)