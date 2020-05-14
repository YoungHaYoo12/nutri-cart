import unittest
from decimal import Decimal
from flask import url_for
from app import create_app, db
from app.foods.views import get_measures_tuple, get_nutrient_multiplier,update_nutrients,clean_food_data
from nutritionix import nutrient_categories

class FlaskClientTestCase(unittest.TestCase):
  def setUp(self):
    self.app = create_app('testing')
    self.app_context = self.app.app_context()
    self.app_context.push()
    db.create_all()
    self.client = self.app.test_client(use_cookies=True)
  
  def tearDown(self):
    db.session.remove()
    db.drop_all()
    self.app_context.pop()

# test class for 'core' blueprint
class FlaskCoreTestCase(FlaskClientTestCase):
  def test_core_index_page(self):
    # Form Validated
    response1 = self.client.post(url_for('core.index'),data= {
      'query': 'brownie'
    })
    self.assertTrue(response1.status_code == 302)

    # Form Not Validated
    response2 = self.client.post(url_for('core.index'),data= {
      'query':''
    })
    self.assertFalse(response2.status_code==302)

# test class for 'foods' blueprint  
class FlaskFoodsTestCase(FlaskClientTestCase):
  def test_foods_list_page(self):
    # Common Filter
    response1 = self.client.get(url_for('foods.list',food_name='Brownie',filter='common'))
    self.assertTrue(response1.status_code == 200)
    data1 = response1.get_data(as_text=True)
    self.assertTrue('Search Results For Brownie' in data1)

    # Branded filter
    response2 = self.client.get(url_for('foods.list',food_name='Brownie',filter='branded'))
    self.assertTrue(response2.status_code == 200)
    data2 = response2.get_data(as_text=True)
    self.assertTrue('Search Results For Brownie' in data2)

    # When filter does not equal "common" or "branded"
    response3 = self.client.get(url_for('foods.list',food_name='Brownie',filter='notCommonOrBranded'))
    self.assertTrue(response3.status_code == 404)
  
  def test_foods_helper_functions(self):
    # get_measures_tuple()
      # When 'alt_measures' is None
    food_info = {
      'serving_weight_grams':Decimal(100),
      'serving_qty':Decimal(10),
      'alt_measures':None,
      'serving_unit':'oz'
    }
    self.assertTrue(get_measures_tuple(food_info) == [('10.00','oz')])

      # When 'alt_measures' is not None
    food_info = {
      'alt_measures': [
        {
          'serving_weight':Decimal(10),
          'qty':Decimal(1),
          'measure':'lb'
        },
        {
          'serving_weight': Decimal(100),
          'qty': Decimal(100),
          'measure': 'g'
        }
      ]
    }
    self.assertTrue(get_measures_tuple(food_info) == [('10.00','lb'),('1.00','g')])

    # get_nutrient_multiplier()
    self.assertTrue(get_nutrient_multiplier(10,20,2) == 4.00)
    self.assertTrue(get_nutrient_multiplier(4,1,3) == 0.75)
    self.assertTrue(type(get_nutrient_multiplier(10,20,2)) is Decimal)
    self.assertTrue(get_nutrient_multiplier('hello',0,10) == 1.00)

    # update_nutrients()
    food_info = {
      'nf_calories':800,
      'nf_sugars':21,
      'nf_cholesterol':10,
      'nf_protein':0,
      'nf_total_fat':0,
      'nf_saturated_fat':0,
      'nf_sodium':0,
      'nf_total_carbohydrate':0,
      'nf_dietary_fiber':0,
      'not_in_categories':2000,
      'not_a_number':'Hello World'
    }
    food_info = update_nutrients(food_info, 2, nutrient_categories)
    self.assertTrue(food_info['nf_calories'] == 1600)
    self.assertTrue(food_info['nf_sugars'] == 42)
    self.assertTrue(food_info['nf_cholesterol'] == 20)
    self.assertTrue(food_info['not_in_categories'] == 2000)
    self.assertTrue(food_info['not_a_number'] == 'Hello World')

    # clean_food_data()
    food_info = {
      'serving_weight_grams':None,
      'serving_qty':'not a float'
    }
    clean_food_data(food_info,nutrient_categories)
    self.assertTrue(food_info['serving_weight_grams'] == 1.00)
    self.assertTrue(food_info['serving_qty'] == 1.00)

    food_info = {
      'nf_calories':2000,
      'nf_sugars':'hello',
      'nf_cholesterol':None,
      'nf_protein':0,
      'nf_total_fat':0,
      'nf_saturated_fat':0,
      'nf_sodium':0,
      'nf_total_carbohydrate':0,
      'nf_dietary_fiber':0,      
      'nf_not_a_category':'should_not_change'
    }
    clean_food_data(food_info,nutrient_categories)
    self.assertTrue(food_info['nf_calories'] == 2000) 
    self.assertTrue(food_info['nf_sugars'] == 0.00) 
    self.assertTrue(food_info['nf_cholesterol'] == 0.00) 
    self.assertTrue(food_info['nf_not_a_category'] == 'should_not_change') 

    food_info = {
      'alt_measures': [
        {
          'serving_weight':10,
          'qty':10
        },
        {
          'serving_weight':'notdecimal',
          'qty':'alsonotdecimal'
        }
      ]
    }
    clean_food_data(food_info,nutrient_categories)
    self.assertTrue(food_info['alt_measures'][0]['serving_weight'] == 10.00)
    self.assertTrue(food_info['alt_measures'][0]['qty'] == 10.00)
    self.assertTrue(food_info['alt_measures'][1]['serving_weight'] == 1.00)
    self.assertTrue(food_info['alt_measures'][1]['serving_weight'] == 1.00)

    # round_food_data
    food_info = {
      'nf_calories':20.20202020,
      'nf_cholesterol':20
    }
    round_food_data(food_info,nutrient_categories)
    self.assertTrue(food_info['nf_calories'] == 20.20)
    self.assertTrue(food_info['nf_cholesterol'] == 20.00)


  def test_foods_common_food(self):
    # Check 404 exception for when food is not in nutritionix database
    resp1a = self.client.get(url_for('foods.common_food',food_name='app'))
    resp1b = self.client.get(url_for('foods.common_food',food_name='apple'))
    self.assertTrue(resp1a.status_code == 404)
    self.assertTrue(resp1b.status_code == 200)

    # Error handling when url parameters "serving_unit" and "serving_qty" are not of correct type
    resp2a = self.client.get(url_for('foods.common_food',food_name='apple',serving_unit='10.0',serving_qty='10.0'))
    resp2b = self.client.get(url_for('foods.common_food',food_name='apple',serving_unit='10.0',serving_qty='not_convertable_to_float'))
    self.assertTrue(resp2a.status_code == 200)
    self.assertTrue(resp2b.status_code == 404)

    # When url parameters serving_unit or serving_qty are None
    resp3 = self.client.get(url_for('foods.common_food',food_name='eggs'))
    self.assertTrue('selected value="50.00"' in resp3.get_data(as_text=True))
    self.assertTrue('value="1.00"' in resp3.get_data(as_text=True))

    # When Form Validates On Submit check redirect
    resp4 = self.client.post(url_for('foods.common_food',food_name='eggs',data = {
      'serving_unit':'50.00',
      'serving_qty':777.00
    }),follow_redirects=True)
    self.assertTrue(resp4.status_code==200)

    # Filling in form data when request method is GET
    resp5 = self.client.get(url_for('foods.common_food',food_name='eggs',serving_unit=63.00,serving_qty=999.00))
    self.assertTrue('selected value="63.00"' in resp5.get_data(as_text=True))
    self.assertTrue('value="999.00"' in resp5.get_data(as_text=True))    

    # Check nutrition updating according to serving_unit and serving_qty
    # (CHECKED AGAINST NUTRITIONIX DATABASE INFORMATION)
    resp6a = self.client.get(url_for('foods.common_food',food_name='eggs',serving_unit=50.00,serving_qty=1.00))
    resp6b = self.client.get(url_for('foods.common_food',food_name='eggs',serving_unit=50.00,serving_qty=2.00))
    resp6c = self.client.get(url_for('foods.common_food',food_name='eggs',serving_unit=38.00,serving_qty=1.00))
    data6a = resp6a.get_data(as_text=True)
    data6b = resp6b.get_data(as_text=True)
    data6c = resp6c.get_data(as_text=True)

    self.assertTrue("Calories: 71.50" in data6a)
    self.assertTrue("Total Carbohydrate: 0.36" in data6a)
    self.assertTrue("Protein: 6.28" in data6a)
    self.assertTrue("Sodium: 71.00" in data6a)
    self.assertTrue("Sugars: 0.19" in data6a)
    self.assertTrue("Total Fat: 4.76" in data6a)
    self.assertTrue("Saturated Fat: 1.56" in data6a)
    self.assertTrue("Dietary Fiber: 0.00" in data6a)

    self.assertTrue("Calories: 143.00" in data6b)
    self.assertTrue("Total Carbohydrate: 0.72" in data6b)
    self.assertTrue("Protein: 12.56" in data6b)
    self.assertTrue("Sodium: 142.00" in data6b)
    self.assertTrue("Sugars: 0.38" in data6b)
    self.assertTrue("Total Fat: 9.52" in data6b)
    self.assertTrue("Saturated Fat: 3.12" in data6b)
    self.assertTrue("Dietary Fiber: 0.00" in data6b)
    
    self.assertTrue("Calories: 54.34" in data6c)
    self.assertTrue("Total Carbohydrate: 0.27" in data6c)
    self.assertTrue("Protein: 4.77" in data6c)
    self.assertTrue("Sodium: 53.96" in data6c)
    self.assertTrue("Sugars: 0.14" in data6c)
    self.assertTrue("Total Fat: 3.62" in data6c)
    self.assertTrue("Saturated Fat: 1.19" in data6c)
    self.assertTrue("Dietary Fiber: 0.00" in data6c)

    # Make sure that result of get_measures_tuple is passed to select form
    resp7 = self.client.get(url_for('foods.common_food',food_name='eggs'))
    data7 = resp7.get_data(as_text=True)
    self.assertTrue('<option value="38.00">small</option>' in data7)
    self.assertTrue('<option value="44.00">medium</option>' in data7)
    self.assertTrue('<option selected value="50.00">large</option>' in data7)
    self.assertTrue('<option value="63.00">jumbo</option>' in data7)
    self.assertTrue('<option value="56.00">extra large</option>' in data7)
    self.assertTrue('<option value="243.00">cup (4.86 large eggs)</option>' in data7)
    self.assertTrue('<option value="1.00">g</option>' in data7)
    self.assertTrue('<option value="28.35">wt. oz</option>' in data7)

  def test_foods_branded_food(self):
    big_mac_id = "513fc9e73fe3ffd40300109f"
    fries_id = "513fc9c9673c4fbc26003ff6"
    # Check 404 exception for when food is not in nutritionix database
    resp1a = self.client.get(url_for('foods.branded_food',nix_item_id='asdfasdfas123'))
    resp1b = self.client.get(url_for('foods.branded_food',nix_item_id=big_mac_id))
    self.assertTrue(resp1a.status_code == 404)
    self.assertTrue(resp1b.status_code == 200)

    # Error handling when url parameters "serving_unit" and "serving_qty" are not of correct type
    resp2a = self.client.get(url_for('foods.branded_food',nix_item_id=big_mac_id,serving_unit='10.00',serving_qty='10.00'))
    resp2b = self.client.get(url_for('foods.branded_food',nix_item_id=big_mac_id,serving_unit='10.00',serving_qty='not_convertable_to_float'))
    self.assertTrue(resp2a.status_code == 200)
    self.assertTrue(resp2b.status_code == 404)

    # When url parameters serving_unit or serving_qty are None
    resp3a = self.client.get(url_for('foods.branded_food',nix_item_id=big_mac_id))
    self.assertTrue('selected value="212.00"' in resp3a.get_data(as_text=True))
    self.assertTrue('value="1.00"' in resp3a.get_data(as_text=True))

    # When also there is a type error, make sure default values are set (serving_weight_grams of food_info is None)
    resp3b = self.client.get(url_for('foods.branded_food',nix_item_id=fries_id))
    self.assertTrue('selected value="1.00"' in resp3b.get_data(as_text=True))
    self.assertTrue('value="1.00"' in resp3b.get_data(as_text=True))

    # When Form Validates On Submit check redirect
    resp4 = self.client.post(url_for('foods.branded_food',nix_item_id=big_mac_id,data = {
      'serving_unit':'212.00',
      'serving_qty':777.00
    }),follow_redirects=True)
    self.assertTrue(resp4.status_code==200)

    # Filling in form data when request method is GET
    resp5 = self.client.get(url_for('foods.branded_food',nix_item_id=big_mac_id,serving_unit=212.00,serving_qty=999.00))
    self.assertTrue('selected value="212.00"' in resp5.get_data(as_text=True))
    self.assertTrue('value="999.00"' in resp5.get_data(as_text=True))    

    # Check nutrition updating according to serving_unit and serving_qty
    # (CHECKED AGAINST NUTRITIONIX DATABASE INFORMATION)
    resp6a = self.client.get(url_for('foods.branded_food',nix_item_id=big_mac_id,serving_unit=212.00,serving_qty=1.00))
    resp6b = self.client.get(url_for('foods.branded_food',nix_item_id=big_mac_id,serving_unit=212.00,serving_qty=2.00))
    data6a = resp6a.get_data(as_text=True)
    data6b = resp6b.get_data(as_text=True)

    self.assertTrue("Calories: 540.00" in data6a)
    self.assertTrue("Total Carbohydrate: 45.00" in data6a)
    self.assertTrue("Protein: 25.00" in data6a)
    self.assertTrue("Sodium: 950.00" in data6a)
    self.assertTrue("Sugars: 9.00" in data6a)
    self.assertTrue("Total Fat: 28.00" in data6a)
    self.assertTrue("Saturated Fat: 10.00" in data6a)
    self.assertTrue("Dietary Fiber: 3.00" in data6a)

    self.assertTrue("Calories: 1080.00" in data6b)
    self.assertTrue("Total Carbohydrate: 90.00" in data6b)
    self.assertTrue("Protein: 50.00" in data6b)
    self.assertTrue("Sodium: 1900.00" in data6b)
    self.assertTrue("Sugars: 18.00" in data6b)
    self.assertTrue("Total Fat: 56.00" in data6b)
    self.assertTrue("Saturated Fat: 20.00" in data6b)
    self.assertTrue("Dietary Fiber: 6.00" in data6b)
    
    # Make sure that result of get_measures_tuple is passed to select form
    resp7 = self.client.get(url_for('foods.branded_food',nix_item_id=big_mac_id))
    data7 = resp7.get_data(as_text=True)
    self.assertTrue('<option selected value="212.00">burger</option>' in data7)