from flask import Blueprint

foods = Blueprint('foods',__name__)

from app.foods import views