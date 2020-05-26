from flask import Blueprint

carts = Blueprint('carts',__name_)

from app.carts import views