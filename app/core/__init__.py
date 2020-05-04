from flask import Blueprint

core = Blueprint('core', __name__)

from app.core import views