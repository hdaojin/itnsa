from flask import  render_template, url_for, current_app
from flask_login import current_user

from . import main

# 注册上下文处理器，使得变量在所有模板中全局可访问. 该函数返回应用菜单的字典
@current_app.context_processor
def inject_nav():
    nav = {
        'main': [
            {'name': '首页', 'url': url_for('main.index')},
            {'name': '关于', 'url': url_for('main.about')}
        ],
        'auth': [
            {'name': '登录', 'url': url_for('auth.login')},
            {'name': '注册', 'url': url_for('auth.register')}
        ],
    }
    # 如果用户已登录
    if current_user.is_authenticated:
        user_nav = {
            'user_logged_in' : [
                {'name': '个人资料', 'url': url_for('auth.profile', user_id=current_user.id)},
                {'name': '注销', 'url': url_for('auth.logout')}
            ],
            'training_log': [
                {'name': '上传日志', 'url': url_for('traininglog.upload_training_log')},
                {'name': '日志列表', 'url': url_for('traininglog.list_training_logs')}
            ],
        }
        nav.update(user_nav)

        # 如果用户是管理员
        if current_user.has_role('admin'):
            admin_nav = {
                'auth_admin': [
                    {'name': '用户列表', 'url': url_for('auth.users')},
                    {'name': '角色列表', 'url': url_for('auth.roles')}
                ],
            }
            nav.update(admin_nav)

    return dict(nav=nav)

@main.route('/')
def index():
    content = "This is the home page"
    return render_template('main/index.html', content=content, title="Home")

@main.route('/about')
def about():
    content = "This is the about page"
    return render_template('main/about.html', content=content, title="About")



