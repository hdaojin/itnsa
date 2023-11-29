# 创建一些辅助函数，用于处理视图函数中的一些通用的操作
from flask import render_template, flash, redirect, url_for
from .service import BaseService

class BaseView:
    service = BaseService

    @classmethod
    def handle_form_submission(cls, form, template, **kwargs):
        if form.validate_on_submit():
            form_data = form.data.copy()
            form_data.pop('submit', None)
            form_data.pop('csrf_token', None)
            cls.service.create(**form_data)
            flash('创建成功', 'success')
            return redirect(url_for(template, **kwargs))
        return render_template('form.html', form=form, **kwargs)
    
    @classmethod
    def list_all(cls, template, **kwargs):
        items = cls.service.get_all()
        print(items)
        return render_template(template, items=cls.service.get_all(), **kwargs)