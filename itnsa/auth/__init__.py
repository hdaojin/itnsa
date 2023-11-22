from flask import Blueprint
from flask_login import LoginManager

auth = Blueprint('auth', __name__, url_prefix='/auth')

# Instaniate a LoginManager object
login_manager = LoginManager()

from .views import *
from .forms import *
