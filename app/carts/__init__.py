from flask import Blueprint

carts = Blueprint('carts',__name__)

from app.carts import views