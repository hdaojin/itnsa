from itnsa.admin import admin
from flask import render_template
from flask_login import login_required
from . import admin_required


@admin.route('/')
@login_required
@admin_required
def index():
    content = "This is the admin home page"
    return render_template('admin/main/index.html', content=content, title="Admin Home")