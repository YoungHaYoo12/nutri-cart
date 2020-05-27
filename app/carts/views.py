from app.carts import carts
from flask_login import current_user,login_required
from flask import render_template

@carts.route('/list/carts')
@login_required
def list():
  carts = current_user.carts
  return render_template('carts/list.html',carts=carts)