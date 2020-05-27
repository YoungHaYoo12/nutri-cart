from app import db
from app.carts import carts
from app.models import Cart
from flask_login import current_user,login_required
from flask import render_template, redirect, url_for

@carts.route('/list/carts')
@login_required
def list():
  carts = current_user.carts
  return render_template('carts/list.html',carts=carts)

@carts.route('/add_cart')
@login_required
def add():
  num_of_carts = len(current_user.carts)
  cart = Cart(num_of_carts + 1)
  cart.user = current_user
  db.session.add(cart)
  db.session.commit()
  return redirect(url_for('carts.list'))