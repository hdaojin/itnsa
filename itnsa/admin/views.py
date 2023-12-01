from functools import wraps
from flask import render_template, redirect, url_for, flash, request, current_app
from flask_login import current_user, login_required

from . import admin
from .forms import TrainingLogModuleForm 
from .forms import TrainingLogTypeForm 
from ..common.service import BaseService
from ..common.views import BaseView
from ..models import TrainingModule, TrainingType, TrainingLog

# Training log module views

class TrainingModuleService(BaseService):
    model = TrainingModule

class TrainingModuleView(BaseView):
    service = TrainingModuleService


def admin_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not current_user.has_role('admin'):
            flash('您没有权限访问该页面', 'danger')
            return redirect(url_for('main.index'))
        return func(*args, **kwargs)
    return decorated_view

@admin.route('/')
@login_required
@admin_required
def index():
    content = "This is the admin home page"
    return render_template('admin/main/index.html', content=content, title="Admin Home")

# Add training module to database
@admin.route('training-module/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_training_module():
    form = TrainingLogModuleForm()
    return TrainingModuleView.handle_form_submission(form, 'admin/form.html', 'admin.index', title="添加训练模块")

# List all training modules
@admin.route('training-module/list')
@login_required
@admin_required
def list_modules():
    return TrainingModuleView.list_all('admin/traininglog/modules.html', title="Training Modules")