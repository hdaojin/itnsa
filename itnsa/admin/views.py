from flask import render_template, redirect, url_for, flash, request, current_app

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


@admin.route('/')
def index():
    content = "This is the admin home page"
    return render_template('admin/main/index.html', content=content, title="Admin Home")

# Add training module to database
@admin.route('module/add', methods=['GET', 'POST'])
def add_module():
    form = TrainingLogModuleForm()
    return TrainingModuleView.handle_form_submission(form, 'admin.index')

# List all training modules
@admin.route('module/list')
def list_modules():
    return TrainingModuleView.list_all('traininglog/modules.html', title="Training Modules")