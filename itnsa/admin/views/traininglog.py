from functools import wraps
from flask import render_template, redirect, url_for, flash, request, current_app
from flask_login import current_user, login_required

from itnsa.admin import admin
from itnsa.admin.forms import TrainingLogModuleForm, TrainingLogTypeForm
from itnsa.common.service import BaseService
from itnsa.common.views import BaseView
from itnsa.models import TrainingModule, TrainingType, TrainingLog
from . import admin_required

# Training log module views

class TrainingModuleService(BaseService):
    model = TrainingModule

class TrainingModuleView(BaseView):
    service = TrainingModuleService


# Add training module to database
@admin.route('training-module/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_training_module():
    form = TrainingLogModuleForm()
    return TrainingModuleView.handle_form_submission(form, 'admin/_form.html', 'admin.index', title="添加训练模块")

# List all training modules
@admin.route('training-module/list')
@login_required
@admin_required
def list_modules():
    return TrainingModuleView.list_all('admin/traininglog/modules.html', title="Training Modules")


# Add training type to database
class TrainingTypeService(BaseService):
    model = TrainingType

class TrainingTypeView(BaseView):
    service = TrainingTypeService

@admin.route('training-type/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_training_type():
    form = TrainingLogTypeForm()
    return TrainingTypeView.handle_form_submission(form, 'admin/_form.html', 'admin.index', title="添加训练类型")

# List all training types
@admin.route('training-type/list')
@login_required
@admin_required
def list_types():
    return TrainingTypeView.list_all('admin/traininglog/types.html', title="Training Types")