from decimal import Decimal, InvalidOperation
from flask import render_template, redirect, url_for,request,abort
from app.foods import foods
from app.foods.forms import FoodServingForm, AddFoodForm
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
    return redirect(url_for('foods.common_food',food_name=food_name,serving_unit=form.serving_unit.datform.submit.dataa,serving_qty=form.serving_qty.data))
  elif add_form.validate_on_submit() and add_form.add.data:
    print('ADD FORM')
  elif request.method == 'GET':
    form.serving_qty.data = Decimal(serving_qty)
    form.serving_unit.data = str(serving_unit)


  return render_template('foods/food.html',food_info=food_info,form=form,add_form=add_form,nutrient_categories_units=nutrient_categories_units)

# Detail Page For Common Food
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
    print("ADD FORM")
  elif request.method == 'GET':
    form.serving_qty.data = Decimal(serving_qty)
    form.serving_unit.data = str(serving_unit)

  return render_template('foods/food.html',food_info=food_info,form=form, add_form=add_form,nutrient_categories_units=nutrient_categories_units)


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
    food_info[category] = food_info[category] * nutrient_multiplier

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