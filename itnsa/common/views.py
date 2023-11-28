# 创建一些辅助函数，用于处理视图函数中的一些通用的操作
from flask import render_template, flash, redirect, url_for

# 处理表单数据
def handle_form_submission(form_class, service, template, **kwargs):
    form = form_class()
    if form.validate_on_submit():
        new_instance = service.model()
        form.populate_obj(new_instance)
        service.create(**new_instance.__dict__)
        flash('添加成功')
        return redirect(url_for(template, **kwargs))
    return render_template('form.html', form=form, **kwargs)

# list all
def list(service, template, **kwargs):
    items = service.list()
    return render_template(template, items=items, **kwargs)