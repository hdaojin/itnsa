from functools import wraps
from flask import render_template, redirect, url_for, flash, request, current_app
from flask_login import current_user, login_required

# 定义一个装饰器，用于检查用户是否具有管理员权限
def admin_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not current_user.has_role('admin'):
            flash('您没有权限访问该页面', 'danger')
            return redirect(url_for('main.index'))
        return func(*args, **kwargs)
    return decorated_view

from . import main, traininglog, auth

