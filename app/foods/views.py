from decimal import Decimal, InvalidOperation
from flask import render_template, redirect, url_for,request,abort, session
from flask_login import login_required, current_user
from app import db
from app.models import Cart, FoodItem
from app.foods import foods
from app.foods.forms import FoodServingForm, AddFoodForm, AddFoodToCartForm
from nutritionix import search_item, get_common_nutrients, get_branded_nutrients, nutrient_categories, nutrient_categories_units

######################################
# VIEW FUNCTIONS

# List all foods resulting from search, filtered by common and branded foods
@foods.route('/list/<food_name>/<filter>')
def list(food_name,filter):
  search_result = search_item(food_name)
  if filter == "common":
    foods = search_result['common']
  elif filter == "branded":
    foods = search_result['branded']
  else:
    abort(404)

  return render_template('foods/list.html',food_name=food_name,foods=foods,filter=filter)
  
# Detail Page For Common Food
@foods.route('/common/<food_name>', methods=['GET','POST'])
@foods.route('/common/<food_name>/<serving_unit>/<serving_qty>',methods=['GET','POST'])
def common_food(food_name, serving_unit=None, serving_qty=None):
  # READ IN FOOD INFO
  food_info = get_common_nutrients(food_name)

  if food_info is None:
    abort(404)
    
  clean_food_data(food_info, nutrient_categories)

  # URL PARAMETER PROCESSING
  if serving_unit is None:
    serving_unit = food_info['serving_weight_grams']
  if serving_qty is None:
    serving_qty = food_info['serving_qty']

  try:
    serving_unit = round(Decimal(serving_unit),2)
    serving_qty = round(Decimal(serving_qty),2)
  except InvalidOperation:
    abort(404)

  measures_tuple = get_measures_tuple(food_info)
  if not is_in_tuple_list(str(serving_unit),measures_tuple):
    abort(404)

  # UPDATE NUTRIENTS
  nutrient_multiplier = get_nutrient_multiplier(food_info['serving_weight_grams'],
  serving_unit, serving_qty)
  update_nutrients(food_info,nutrient_multiplier,nutrient_categories)
  round_food_data(food_info,nutrient_categories)

  # FORM PROCESSING
  form = FoodServingForm()
  add_form=AddFoodForm()
  form.serving_unit.choices = measures_tuple

  if form.validate_on_submit() and form.submit.data:
    return redirect(url_for('foods.common_food',food_name=food_name,serving_unit=form.serving_unit.data,serving_qty=form.serving_qty.data))
  elif add_form.validate_on_submit() and add_form.add.data:
    session['food_info'] = food_info
    # get string representation of serving_unit
    session['serving_unit'] = get_str_serving_unit(measures_tuple,str(round(serving_unit,2)))
    session['serving_qty'] = serving_qty
    return redirect(url_for('foods.add_food'))
  elif request.method == 'GET':
    form.serving_qty.data = Decimal(serving_qty)
    form.serving_unit.data = str(serving_unit)


  return render_template('foods/food.html',food_info=food_info,form=form,add_form=add_form,nutrient_categories_units=nutrient_categories_units)

# Detail Page For Branded Food
@foods.route('/branded/<nix_item_id>', methods=['GET','POST'])
@foods.route('/branded/<nix_item_id>/<serving_unit>/<serving_qty>',methods=['GET','POST'])
def branded_food(nix_item_id, serving_unit=None, serving_qty=None):
  # READ IN FOOD INFO
  food_info = get_branded_nutrients(nix_item_id)

  if food_info is None:
    abort(404)
    
  clean_food_data(food_info, nutrient_categories)

  # URL PARAMETER PROCESSING
  if serving_unit is None:
    serving_unit = food_info['serving_weight_grams']
  if serving_qty is None:
    serving_qty = food_info['serving_qty']

  try:
    serving_unit = round(Decimal(serving_unit),2)
    serving_qty = round(Decimal(serving_qty),2)
  except InvalidOperation:
    abort(404)

  measures_tuple = get_measures_tuple(food_info)
  if not is_in_tuple_list(str(serving_unit),measures_tuple):
    abort(404)

  # UPDATE NUTRIENTS
  nutrient_multiplier = get_nutrient_multiplier(food_info['serving_weight_grams'],
  serving_unit, serving_qty)
  update_nutrients(food_info,nutrient_multiplier,nutrient_categories)
  round_food_data(food_info,nutrient_categories)

  # FORM PROCESSING
  form = FoodServingForm()
  add_form = AddFoodForm()
  form.serving_unit.choices = measures_tuple

  if form.validate_on_submit() and form.submit.data:
    return redirect(url_for('foods.branded_food',nix_item_id=nix_item_id,serving_unit=form.serving_unit.data,serving_qty=form.serving_qty.data))
  elif add_form.validate_on_submit() and add_form.add.data:
    session['food_info'] = food_info
    # get string representation of serving_unit
    session['serving_unit'] = get_str_serving_unit(measures_tuple,str(round(serving_unit,2)))
    session['serving_qty'] = serving_qty
    return redirect(url_for('foods.add_food'))
  elif request.method == 'GET':
    form.serving_qty.data = Decimal(serving_qty)
    form.serving_unit.data = str(serving_unit)

  return render_template('foods/food.html',food_info=food_info,form=form, add_form=add_form,nutrient_categories_units=nutrient_categories_units)

@foods.route('/add_food', methods=['POST','GET'])
@login_required
def add_food():
  form = AddFoodToCartForm()
  
  # form processing
  cart_id_tuple = []
  carts = current_user.carts.order_by(Cart.id.asc()).all()
  for i in range(len(carts)):
    cart_id_tuple.append((str(carts[i].id),i+1))
  form.cart_id.choices = cart_id_tuple
  
  if form.validate_on_submit():
    # get cart
    cart = Cart.query.get_or_404(int(form.cart_id.data))
    
    # create food and add to cart
    food_info = session.get('food_info')
    food = FoodItem(name=food_info['food_name'],
    img_url=food_info['photo']['thumb'],
    nf_calories=food_info['nf_calories'],
    nf_total_fat=food_info['nf_total_fat'],
    nf_saturated_fat=food_info['nf_saturated_fat'],
    nf_cholesterol=food_info['nf_cholesterol'],
    nf_sodium=food_info['nf_sodium'],
    nf_total_carbohydrate=food_info['nf_total_carbohydrate'],
    nf_dietary_fiber=food_info['nf_dietary_fiber'],
    nf_sugars=food_info['nf_sugars'],
    nf_protein=food_info['nf_protein'],
    serving_unit=session.get('serving_unit'),
    serving_qty=session.get('serving_qty')
    )
    food.cart = cart
    db.session.add(food)
    db.session.commit()
    
    return redirect(url_for('carts.list'))
  
  return render_template('foods/add_food.html',form=form)
######################################
# HELPER FUNCTIONS

# Construct tuple of measures (serving weight/qty, measure unit) for a food product 
def get_measures_tuple(food_info):
  if food_info.get('alt_measures') is None:
    single_serving_weight = food_info['serving_weight_grams']/food_info['serving_qty']
    single_serving_weight = round(single_serving_weight,2)
    measures_tuple = [(str(single_serving_weight),food_info['serving_unit'])]

  else:
    measures_tuple = [
      (str(round(i['serving_weight']/i['qty'],2)),i['measure']) for i in food_info['alt_measures']
    ]

  return measures_tuple

# Calculate new nutrient multiplier when serving unit and quantity change
def get_nutrient_multiplier(original_serving_weight,new_serving_weight, qty):
  try:
    new_serving_weight = Decimal(new_serving_weight)
    original_serving_weight = Decimal(original_serving_weight)
    qty = Decimal(qty)
  except InvalidOperation:
    return Decimal(1)
  except TypeError:
    return Decimal(1)

  return new_serving_weight/original_serving_weight*qty

# Update nutrient categories by nutrient multiplier when serving unit and quantity change
def update_nutrients(food_info, nutrient_multiplier, nutrient_categories):
  for category in nutrient_categories:
    food_info[category] = Decimal( food_info[category] * nutrient_multiplier)

# function to clean up "None" values in food_info
def clean_food_data(food_info, nutrient_categories):
  # serving_weight_grams & serving_qty
  try:
    food_info['serving_weight_grams'] = Decimal(food_info.get('serving_weight_grams'))
  except InvalidOperation:
    food_info['serving_weight_grams'] = Decimal(1)
  except TypeError:
    food_info['serving_weight_grams'] = Decimal(1)
  try:
    food_info['serving_qty'] = Decimal(food_info.get('serving_qty'))
  except InvalidOperation:
    food_info['serving_qty'] = Decimal(1)
  except TypeError:
    food_info['serving_qty'] = Decimal(1)

  # alt measures 
  if food_info.get('alt_measures') is not None:
    for i in food_info['alt_measures']:
      try:
        i['serving_weight'] = Decimal(i.get('serving_weight'))
      except InvalidOperation:
        i['serving_weight'] = Decimal(1)
      except TypeError:
        i['serving_weight'] = Decimal(1)
      try:
        i['qty'] = Decimal(i.get('qty'))
      except InvalidOperation:
        i['qty'] = Decimal(1)
      except TypeError:
        i['qty'] = Decimal(1)

  # nutrient categories
  for category in nutrient_categories:
    try:
      food_info[category] = Decimal(food_info.get(category))
    except InvalidOperation:
      food_info[category] = Decimal(0)
    except TypeError:
      food_info[category] = Decimal(0)

# function to round nutrient category values 
def round_food_data(food_info,nutrient_categories):
  for category in nutrient_categories:
    food_info[category] = round(food_info[category],2)

# function to check if argument is contained in list of tuples
def is_in_tuple_list(arg,tuple_list):
  for tuple in tuple_list:
    if arg == tuple[0]:
      return True
  
  return False

# function to retrieve specific serving_unit from measures_tuple
def get_str_serving_unit(measures_tuple,serving_unit):
  for measure in measures_tuple:
    if measure[0] == serving_unit:
      return measure[1]
  return None