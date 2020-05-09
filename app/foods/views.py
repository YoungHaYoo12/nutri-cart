from flask import render_template
from app.foods import foods
from nutritionix import search_item

# List all foods resulting from search, filtered by common and branded foods
@foods.route('/list/<food_name>/<filter>')
def list(food_name,filter):
  search_result = search_item(food_name)
  if filter == "common":
    foods = search_result['common']
  else:
    foods = search_result['branded']

  return render_template('foods/list.html',food_name=food_name,foods=foods)

