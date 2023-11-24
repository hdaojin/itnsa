from flask import Blueprint

traininglog = Blueprint('traininglog', __name__, url_prefix='/traininglog')

from .views import *