from flask import  render_template, url_for, current_app
from flask_login import current_user

from . import main

@current_app.context_processor
def inject_nav():
    nav = [
        {'name': 'Home', 'url': url_for('main.index')},
        {'name': 'About', 'url': url_for('main.about')},
        {'name': 'Upload', 'url': url_for('upload.upload_training_log')},
        {'name': 'Training Log', 'url': url_for('upload.training_logs')},
    ]

    # 如果用户已登录并且是管理员
    if current_user.is_authenticated and current_user.has_role('admin'):
        nav.append({'name': 'Users', 'url': url_for('auth.users')})

    return dict(nav=nav)

@current_app.context_processor
def inject_auth_nav():
    register = {'name': '注册', 'url': url_for('auth.register')}
    login = {'name': '登录', 'url': url_for('auth.login')}
    if current_user.is_authenticated:
        logged_in = [
            {'name': '个人资料', 'url': url_for('auth.profile', user_id=current_user.id)},
            {'name': '注销', 'url': url_for('auth.logout')}
        ]
        return dict(logged_in=logged_in)
    return dict(register=register, login=login)

@main.route('/')
def index():
    content = "This is the home page"
    return render_template('main/index.html', content=content, title="Home")

@main.route('/about')
def about():
    content = "This is the about page"
    return render_template('main/about.html', content=content, title="About")



