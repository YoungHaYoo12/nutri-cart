# Functions to interact with Nutritionix API for nutrition information retrieval

import os, requests 

headers = {
  'x-app-id' : os.environ.get('X_APP_ID'),
  'x-app-key' : os.environ.get('X_APP_KEY')
}

"""
Description from Nutritionix API Documentation:

When you hit the /search/instant endpoint it returns two arrays: common and branded foods. To get the nutrition information for common foods, take the food_name that is returned from any item in the "common" array, e.g. "Big Mac" and POST that as the query to our /natural/nutrients endpoint. To get the nutrition information for branded foods take the value of the "nix_item_id" attribute from any of the objects in the "branded" array and hit the /search/item endpoint 

"""

url_search_instant = "https://trackapi.nutritionix.com/v2/search/instant"
url_natural_nutrients = "https://trackapi.nutritionix.com/v2/natural/nutrients"
url_search_item = "https://trackapi.nutritionix.com/v2/search/item"

def search_item(food_name):
  """Retrieves basic food information for foods related to query.

  Retrieves basic food information for foods related to query via a GET request to the search/instant endpoint.

  Parameters:
    food_name (str): food name to be queried for.
  
  Returns:
    dict: JSON data containing basic food information for foods related to query.

  """

  body = {
        "query":food_name,
  }

  response = requests.get(url_search_instant,headers=headers,params=body)
  return response.json()

def get_common_nutrients(food_name):
  """Retrieves nutrition information for common foods. 

  Retrives nutrition information for common foods related to query via a POST request to the natural/nutrients endpoint.

  Parameters:
    food_name (str): food name to be queried for.
  
  Returns:
    dict: Contains nutrition information (e.g. calories) with specific nutrients as keys and their respective amounts as values

  """

  body = {
          "query":food_name,
  }

  response = requests.post(url_natural_nutrients,headers=headers,data=body)
  nutrients = response.json()['foods'][0]
  return nutrients

def get_branded_nutrients(nix_item_id):
  """Retrieves nutrition information for branded foods. 

  Retrives nutrition information for branded foods related to query via a GET request to the search/item endpoint.

  Parameters:
    nix_item_id (str): id related to specific branded foods.
  
  Returns:
    dict: Contains nutrition information (e.g. calories) with specific nutrients as keys and their respective amounts as values

  """
  body = {
      "nix_item_id":nix_item_id,
  }
  response = requests.get(url_search_item,headers=headers,params=body)
  nutrients = response.json()['foods'][0]
  return nutrients

# Contains nutrient categories to display
nutrient_categories = ['serving_qty', 'serving_unit','nf_serving_weight_grams', 'nf_calories', 'nf_total_fat',
'nf_saturated_fat','nf_cholesterol','nf_sodium','nf_total_carbohydrate','nf_dietary_fiber','nf_sugars','nf_protein']
