from app import db
from app.carts import carts
from app.models import Cart
from flask_login import current_user,login_required
from flask import render_template, redirect, url_for, request

@carts.route('/list/carts')
@login_required
def list():
  page = request.args.get('page',1,type=int)
  pagination = current_user.carts.paginate(page,per_page=4)
  carts = pagination.items
  return render_template('carts/list.html',carts=carts,pagination=pagination)

@carts.route('/add_cart')
@login_required
def add():
  num_of_carts = len(current_user.carts.all())
  cart = Cart(num_of_carts + 1)
  cart.user = current_user
  db.session.add(cart)
  db.session.commit()
  return redirect(url_for('carts.list'))

@carts.route('/delete/<int:id>')
def delete(id):
  cart = Cart.query.get_or_404(id)
  db.session.delete(cart)
  db.session.commit()
  return redirect(url_for('carts.list'))