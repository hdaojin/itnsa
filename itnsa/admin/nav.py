from flask import url_for, render_template, current_app
from itnsa import main
from itnsa.admin import admin

# 注册上下文处理器，使得变量在所有模板中全局可访问. 该函数返回应用菜单的字典
@admin.context_processor
def inject_admin_nav():
    admin_nav = {
        'main': [
            {'name': '网站首页', 'url': url_for('main.index')},
            {'name': '管理面板', 'url': url_for('admin.index')},
            {'name': '训练模块', 'url': url_for('admin.list_modules')},
            {'name': '添加训练模块', 'url': url_for('admin.add_training_module')},
            {'name': '用户列表', 'url': url_for('admin.users')},
            {'name': '角色列表', 'url': url_for('admin.roles')},
            {'name': '生成注册链接', 'url': url_for('admin.gen_reg_link')},
        ],
    }
    return dict(admin_nav=admin_nav)