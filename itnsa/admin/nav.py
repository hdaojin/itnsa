from flask import url_for, render_template, current_app
from flask_login import current_user
from itnsa import main
from itnsa.admin import admin

# 注册上下文处理器，使得变量在所有模板中全局可访问. 该函数返回应用菜单的字典
@admin.context_processor
def inject_admin_nav():
    main_nav = [
        {'name': '网站首页', 'url': url_for('main.index')},
        # {'name': '修改密码', 'url': url_for('admin.change_password', id=current_user.id)},
    ]
    administator_nav = [
        {'name': '管理面板', 'url': url_for('admin.index')},
        {'name': '训练类型', 'url': url_for('admin.list_types')},
        {'name': '添加训练类型', 'url': url_for('admin.add_training_type')},
        {'name': '训练模块', 'url': url_for('admin.list_modules')},
        {'name': '添加训练模块', 'url': url_for('admin.add_training_module')},
        {'name': '用户列表', 'url': url_for('admin.users')},
        {'name': '角色列表', 'url': url_for('admin.roles')},
        {'name': '注册链接', 'url': url_for('admin.reg_link')}
    ]

    if current_user.is_authenticated:
        if current_user.has_role('admin'):
            main_nav.extend(administator_nav)
        return dict(main_nav=main_nav)
