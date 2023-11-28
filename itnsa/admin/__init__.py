from flask import Blueprint

# 创建一个 Blueprint 实例
admin = Blueprint('admin', __name__, url_prefix='/admin', template_folder='templates', static_folder='static')

# 导入视图。这一步很重要，因为它让 Flask 知道这些视图属于 auth 蓝图。
from . import views