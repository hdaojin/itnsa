from flask import render_template, redirect, url_for, flash, request, current_app

from . import admin
from .forms import TrainingLogModuleForm as tlmf
from .forms import TrainingLogTypeForm as tltf
from ..common.service import TrainingLogModuleService as tlms
from ..common.service import TrainingLogTypeService 
from ..common.views import handle_form_submission, list
from ..models import db

# Training log module views
tlms = tlms(db)

@admin.route('/')
def index():
    content = "This is the admin home page"
    return render_template('main/index.html', content=content, title="Admin Home")

# Add training log module to database
@admin.route('/module/add', methods=['GET', 'POST'])
def add_traininglog_module():
    return handle_form_submission(tlmf, tlms, 'admin.list_traininglog_modules', title='添加训练模块')

# List training log modules from database
@admin.route('/module/list')
def list_traininglog_modules():
    return list(tlms, 'traininglog/modules.html', title='训练日志模块列表')


# Delete training log module from database
@admin.route('/module/delete/<int:training_log_module_id>')
def delete_traininglog_module(training_log_module_id):
    tlms.deleteß(training_log_module_id)
    return redirect(url_for('admin.list_traininglog_modules'))






