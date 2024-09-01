# 创建一些辅助函数，用于处理视图函数中的一些通用的操作
from flask import render_template, flash, redirect, url_for, current_app
from itsdangerous import URLSafeTimedSerializer
import mistune, frontmatter

from .service import BaseService

class BaseView:
    service = BaseService

    @classmethod
    def handle_form_submission(cls, form, template, view=None, **kwargs):
        if form.validate_on_submit():
            form_data = form.data.copy()
            form_data.pop('submit', None)
            form_data.pop('csrf_token', None)
            cls.service.create(**form_data)
            flash('创建成功', 'success')
            return redirect(url_for(view, **kwargs))
        return render_template(template, form=form, **kwargs)
    
    @classmethod
    def list_all(cls, template, **kwargs):
        items = cls.service.get_all()
        print(items)
        return render_template(template, items=cls.service.get_all(), **kwargs)


# 通过加密令牌生成注册链接
# 生成的链接有效期为12小时
link_age = 43200

def generate_registration_link():
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    token = serializer.dumps('register', salt=current_app.config['SECRET_SALT'])
    link = url_for('auth.register', token=token, _external=True)
    return link, link_age

def validate_registration_link(token, max_age=link_age):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        data = serializer.loads(token, salt=current_app.config['SECRET_SALT'], max_age=max_age)
        return data == 'register'
    except:
        return False

def mistune_to_html(markdown_file):
    """Convert markdown to html."""
    with open(markdown_file, 'r', encoding='utf-8') as f:
        content = f.read()
        metadata, content = frontmatter.parse(content)        
        html = mistune.html(content)
    return html, metadata