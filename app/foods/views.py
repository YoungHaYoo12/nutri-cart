from flask import render_template, redirect, url_for,request,abort
from app.foods import foods
from app.foods.forms import FoodServingForm
from nutritionix import search_item, get_common_nutrients, get_branded_nutrients, nutrient_categories

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

  return render_template('foods/list.html',food_name=food_name,foods=foods)

# Detail Page For Common Food
@foods.route('/common/<food_name>', methods=['GET','POST'])
@foods.route('/common/<food_name>/<serving_unit>/<serving_qty>',methods=['GET','POST'])
def common_food(food_name, serving_unit=None, serving_qty=None):
  # Read in Food Information
  food_info = get_common_nutrients(food_name)

  # 404 exception if food is not in nutritionix database
  if food_info is None:
    abort(404)

  if serving_unit is None:
    try:
      serving_unit = float(food_info['serving_weight_grams'])
    except TypeError:
      serving_unit = 1
  if serving_qty is None:
    try:
      serving_qty = float(food_info['serving_qty'])
    except TypeError:
      serving_qty = 1

  # catch if serving_unit and serving_qty url parameters are not of the correct type
  try:
    nutrient_multiplier = get_nutrient_multiplier(food_info['serving_weight_grams'],serving_unit,serving_qty)
  except ValueError:
    abort(404)
  food_info = update_nutrients(food_info,nutrient_multiplier,nutrient_categories)

  # Form Processing
  form = FoodServingForm()
  measures_tuple = get_measures_tuple(food_info)
  form.serving_unit.choices = measures_tuple
  if form.validate_on_submit():
    return redirect(url_for('foods.common_food',food_name=food_name,serving_unit=form.serving_unit.data,serving_qty=form.serving_qty.data))
  elif request.method == 'GET':
    try:
      form.serving_qty.data = float(serving_qty)
      form.serving_unit.data = str(serving_unit)
    except:
      pass

  return render_template('foods/food.html',food_info=food_info,form=form)

# Detail Page For Branded Food
@foods.route('/branded/<nix_item_id>', methods=['GET','POST'])
@foods.route('/branded/<nix_item_id>/<serving_unit>/<serving_qty>',methods=['GET','POST'])
def branded_food(nix_item_id, serving_unit=None, serving_qty=None):
  # Read in Food Information
  food_info = get_branded_nutrients(nix_item_id)

  # 404 exception if food is not in nutritionix database
  if food_info is None:
    abort(404)
    
  if serving_unit is None:
    try:
      serving_unit = float(food_info['serving_weight_grams'])
    except TypeError:
      serving_unit = 1
  if serving_qty is None:
    try:
      serving_qty = float(food_info['serving_qty'])
    except:
      serving_qty = 1

  # catch if serving_unit and serving_qty url parameters are not of the correct type
  try:
    nutrient_multiplier = get_nutrient_multiplier(food_info['serving_weight_grams'],serving_unit,serving_qty)
  except ValueError:
    abort(404)

  food_info = update_nutrients(food_info,nutrient_multiplier,nutrient_categories)

  # Form Processing
  form = FoodServingForm()
  measures_tuple = get_measures_tuple(food_info)
  form.serving_unit.choices = measures_tuple
  if form.validate_on_submit():
    return redirect(url_for('foods.branded_food',nix_item_id=nix_item_id,serving_unit=form.serving_unit.data,serving_qty=form.serving_qty.data))
  elif request.method == 'GET':
    try:
      form.serving_qty.data = float(serving_qty)
      form.serving_unit.data = str(serving_unit)
    except:
      pass

  return render_template('foods/food.html',food_info=food_info,form=form)
  
######################################
# HELPER FUNCTIONS

# Construct tuple of measures (serving weight/qty, measure unit) for a food product 
def get_measures_tuple(food_info):
  if food_info['alt_measures'] is None:
    try:
      #if food_info.get('serving_weight_grams') is None:
       # measures_tuple = 
      measures_tuple = [(str(float(food_info['serving_weight_grams'])/float(food_info['serving_qty'])),food_info['serving_unit'])]
    except TypeError:
      measures_tuple = [('1','serving')]
  else:
    try:
      measures_tuple = [(str(float(i['serving_weight'])/float(i['qty'])),i['measure']) for i in food_info['alt_measures']]
    except TypeError:
      measures_tuple = None

  return measures_tuple

# Calculate new nutrient multiplier when serving unit and quantity change
def get_nutrient_multiplier(original_serving_weight,new_serving_weight, qty):
  try:
    new_serving_weight = float(new_serving_weight)
    original_serving_weight = float(original_serving_weight)
    qty = float(qty)
  except TypeError:
    return 1

  return new_serving_weight/original_serving_weight*qty

# Update nutrient categories by nutrient multiplier when serving unit and quantity change
def update_nutrients(food_info, nutrient_multiplier, nutrient_categories):
  for category in nutrient_categories:
    if (not category in food_info.keys()):
      continue

    if type(food_info[category]) != int and type(food_info[category]) != float:
      continue
    
    food_info[category] = food_info[category] * nutrient_multiplier
  
  return food_info