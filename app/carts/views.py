from app import db
from app.carts import carts
from app.models import Cart, User
from flask_login import current_user,login_required
from flask import render_template, redirect, url_for, request, abort
from nutritionix import nutrient_categories_units

@carts.route('/list/<username>')
@carts.route('/list/<username>/sort_by/<nutrient>')
@login_required
def list(username,nutrient=None):
  page = request.args.get('page',1,type=int)

  # retrive user
  user = User.query.filter_by(username=username).first()
  if user is None:
    abort(404)

  # Order Carts (If sorting argument provided)
  if nutrient is None:
    query = user.carts.order_by(Cart.id.asc())
  else:
    sort_options = {
      'nf_calories' : Cart.nf_calories,
      'nf_total_fat' : Cart.nf_total_fat,
      'nf_saturated_fat' : Cart.nf_saturated_fat,
      'nf_cholesterol' : Cart.nf_cholesterol,
      'nf_sodium' : Cart.nf_sodium,
      'nf_total_carbohydrate' : Cart.nf_total_carbohydrate,
      'nf_dietary_fiber' : Cart.nf_dietary_fiber,
      'nf_sugars' : Cart.nf_sugars,
      'nf_protein' : Cart.nf_protein
    } 
    query = user.carts.order_by(sort_options[nutrient].desc())
  pagination = query.paginate(page,per_page=4)

  carts = pagination.items
  prev_cart_num = (page-1)*4
  cart_counter = [prev_cart_num+1,prev_cart_num+2,prev_cart_num+3,prev_cart_num+4]
  return render_template('carts/list.html',carts=carts,pagination=pagination,cart_counter=cart_counter,nutrient_categories_units=nutrient_categories_units,
  nutrient=nutrient,user=user)

@carts.route('/cart/<int:id>')
@login_required
def cart(id):
  cart = Cart.query.get_or_404(id)
  foods = cart.foods.all()
  return render_template('carts/cart.html', cart=cart,foods=foods,nutrient_categories_units=nutrient_categories_units)

@carts.route('/add_cart')
@login_required
def add():
  cart = Cart()
  cart.user = current_user
  db.session.add(cart)
  db.session.commit()
  return redirect(url_for('carts.list',username=current_user.username))

@carts.route('/delete/<int:id>')
@login_required
def delete(id):
  cart = Cart.query.get_or_404(id)
  db.session.delete(cart)
  db.session.commit()
  return redirect(url_for('carts.list',username=current_user.username))