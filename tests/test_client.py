import unittest
from datetime import datetime
from decimal import Decimal
from flask import url_for
from flask_login import current_user
from app import create_app, db
from app.foods.views import get_measures_tuple, get_nutrient_multiplier,update_nutrients,clean_food_data,round_food_data,is_in_tuple_list,get_str_serving_unit
from app.models import User, Cart, FoodItem
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
  def test_core_index(self):
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
  
  def test_core_users(self):
    # Form Validated
    response1 = self.client.post(url_for('core.users'),data= {
      'query': 'one'
    })
    self.assertTrue(response1.status_code == 302)

    # Form Not Validated
    response2 = self.client.post(url_for('core.users'),data= {
      'query':''
    })
    self.assertFalse(response2.status_code==302)

    # When queried user exists
    user = User(email='one@one.com',username='one',password='one')
    db.session.add(user)
    db.session.commit()
    response3 = self.client.get(url_for('core.users',username='one'))
    data3 = response3.get_data(as_text=True)
    self.assertTrue('one' in data3)
    
    # When queried user does not exist
    response4 = self.client.get(url_for('core.users',username='two'))
    data4 = response4.get_data(as_text=True)
    self.assertTrue('No Results Returned.' in data4)
  
  def test_core_follow(self):
    user1 = User(email='one@one.com',username='one',password='one')
    user2 = User(email='two@two.com',username='two',password='two')
    db.session.add_all([user1,user2])
    db.session.commit()
    
    with self.client:
      self.client.post(url_for('auth.login'), data=
      { 
        'email': 'one@one.com', 
        'username':'one',
        'password': 'one' 
      }
      )

      # test redirect when user does not exist
      response1 = self.client.get(url_for('core.follow',username='ten'),follow_redirects=True)
      data1 = response1.get_data(as_text=True)
      self.assertTrue('Invalid User' in data1)
      self.assertTrue('search-box' in data1)

      # successful follow request
      response2 = self.client.get(url_for('core.follow',username='two'),follow_redirects=True)
      data2 = response2.get_data(as_text=True)
      self.assertTrue('You are now following two' in data2)
      one = User.query.filter_by(username='one').first()
      two = User.query.filter_by(username='two').first()
      self.assertTrue(one.is_following(two))
      self.assertTrue(two.is_followed_by(one))

      # test redirect when current user is already following user
      response3 = self.client.get(url_for('core.follow',username='two'),follow_redirects=True)
      data3 = response3.get_data(as_text=True)
      self.assertTrue('You are already following this user' in data3)
      self.assertTrue(one.is_following(two))
      self.assertTrue(two.is_followed_by(one))

  def test_core_unfollow(self):
    user1 = User(email='one@one.com',username='one',password='one')
    user2 = User(email='two@two.com',username='two',password='two')
    db.session.add_all([user1,user2])
    db.session.commit()
    user1.follow(user2)
    db.session.commit()

    with self.client:
      self.client.post(url_for('auth.login'), data=
      { 
        'email': 'one@one.com', 
        'username':'one',
        'password': 'one' 
      }
      )

      # test redirect when user does not exist
      response1 = self.client.get(url_for('core.unfollow',username='ten'),follow_redirects=True)
      data1 = response1.get_data(as_text=True)
      self.assertTrue('Invalid User' in data1)
      self.assertTrue('search-box' in data1)

      # successful unfollow request
      one = User.query.filter_by(username='one').first()
      two = User.query.filter_by(username='two').first()
      self.assertTrue(one.is_following(two))
      self.assertTrue(two.is_followed_by(one))
      response2 = self.client.get(url_for('core.unfollow',username='two'),follow_redirects=True)
      data2 = response2.get_data(as_text=True)
      self.assertTrue('You are no longer following two' in data2)
      self.assertFalse(one.is_following(two))
      self.assertFalse(two.is_followed_by(one))

      # test redirect when current user is not currently following user
      response3 = self.client.get(url_for('core.unfollow',username='two'),follow_redirects=True)
      data3 = response3.get_data(as_text=True)
      self.assertTrue('You are currently not following this user' in data3)
      self.assertFalse(one.is_following(two))
      self.assertFalse(two.is_followed_by(one))

# test class for 'foods' blueprint  
class FlaskFoodsTestCase(FlaskClientTestCase):
  def test_foods_list(self):
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
    self.assertTrue(get_nutrient_multiplier(None,None,None) == Decimal(1))

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
    update_nutrients(food_info, 2, nutrient_categories)
    self.assertTrue(food_info['nf_calories'] == 1600)
    self.assertTrue(food_info['nf_sugars'] == 42)
    self.assertTrue(food_info['nf_cholesterol'] == 20)
    self.assertTrue(food_info['not_in_categories'] == 2000)
    self.assertTrue(food_info['not_a_number'] == 'Hello World')

    # clean_food_data()
    food_info = {
      'serving_weight_grams':None,
      'serving_qty':'not a float',
    }
    clean_food_data(food_info,nutrient_categories)
    self.assertTrue(food_info['serving_weight_grams'] == 1.00)
    self.assertTrue(food_info['serving_qty'] == 1.00)

    food_info = {
      'serving_weight_grams':'not a dec',
      'serving_qty':None,
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
        },
        {
          'serving_weight':None,
          'qty':None
        }
      ]
    }
    clean_food_data(food_info,nutrient_categories)
    self.assertTrue(food_info['alt_measures'][0]['serving_weight'] == 10.00)
    self.assertTrue(food_info['alt_measures'][0]['qty'] == 10.00)
    self.assertTrue(food_info['alt_measures'][1]['serving_weight'] == 1.00)
    self.assertTrue(food_info['alt_measures'][1]['serving_weight'] == 1.00)
    self.assertTrue(food_info['alt_measures'][2]['serving_weight'] == 1.00)
    self.assertTrue(food_info['alt_measures'][2]['serving_weight'] == 1.00)
    # round_food_data
    food_info = {
      'nf_calories':20.20202020,
      'nf_cholesterol':20,
      'nf_sugars':88.88,
      'nf_protein':0,
      'nf_total_fat':0,
      'nf_saturated_fat':0,
      'nf_sodium':0,
      'nf_total_carbohydrate':0,
      'nf_dietary_fiber':0,      
    }
    round_food_data(food_info,nutrient_categories)
    self.assertTrue(food_info['nf_calories'] == 20.20)
    self.assertTrue(food_info['nf_cholesterol'] == 20.00)

    # is_in_tuple_list
    tuple_list = [
      ('1.11','arg2'),
      ('2.22','arg2'),
      ('3.33','arg2')
    ]
    self.assertTrue(is_in_tuple_list('1.11',tuple_list))
    self.assertTrue(is_in_tuple_list('2.22',tuple_list))
    self.assertTrue(is_in_tuple_list('3.33',tuple_list))
    self.assertFalse(is_in_tuple_list('1.22',tuple_list))

    # get_str_serving_unit
    tuple1 = ('42.0','serving1')
    tuple2 = ('21.00','serving2')
    measures_tuple = [tuple1, tuple2]
    self.assertTrue(get_str_serving_unit(measures_tuple,'42.0') == 'serving1')
    self.assertTrue(get_str_serving_unit(measures_tuple,'21.00') == 'serving2')

  def test_foods_delete_food(self):
    user = User(email='one@one.com',username='one',password='one')
    user2 = User(email='two@two.com',username='two',password='two')
    cart = Cart()
    cart2 = Cart()
    food1 = FoodItem(name='food1',
    img_url="",
    nf_calories=Decimal(1),
    nf_total_fat=Decimal(2),
    nf_cholesterol=Decimal(3),
    nf_saturated_fat=Decimal(4),
    nf_sodium=Decimal(5),
    nf_total_carbohydrate=Decimal(6),
    nf_dietary_fiber=Decimal(7),
    nf_sugars=Decimal(8),
    nf_protein=Decimal(9),
    serving_qty=Decimal(1),
    serving_unit="Serving")

    food2 = FoodItem(name='food2',
    img_url="",
    nf_calories=Decimal(1),
    nf_total_fat=Decimal(2),
    nf_cholesterol=Decimal(3),
    nf_saturated_fat=Decimal(4),
    nf_sodium=Decimal(5),
    nf_total_carbohydrate=Decimal(6),
    nf_dietary_fiber=Decimal(7),
    nf_sugars=Decimal(8),
    nf_protein=Decimal(9),
    serving_qty=Decimal(1),
    serving_unit="Serving")
    food1.cart = cart
    food2.cart = cart2
    cart.user = user
    cart2.user = user2
    db.session.add_all([user,user2,cart,cart2,food1,food2])
    db.session.commit()

    with self.client:
      self.client.post(url_for('auth.login'), data=
      { 
        'email': 'one@one.com', 
        'username':'one',
        'password': 'one' 
      }
      )

      # delete food
      self.client.get(url_for('foods.delete_food',id=1))
      cart = current_user.carts.first()
      self.assertTrue(len(cart.foods.all()) == 0)

      # 404 error if food does not exist
      response1 = self.client.get(url_for('foods.delete_food',id=100))
      self.assertTrue(response1.status_code == 404)

      # 403 error if food does not belong to user  
      response2 = self.client.get(url_for('foods.delete_food',id=2))
      self.assertTrue(response2.status_code == 403)

  def test_foods_common_food(self):
    # Check 404 exception for when food is not in nutritionix database
    resp1a = self.client.get(url_for('foods.common_food',food_name='app'))
    resp1b = self.client.get(url_for('foods.common_food',food_name='apple'))
    self.assertTrue(resp1a.status_code == 404)
    self.assertTrue(resp1b.status_code == 200)

    # Error handling when url parameters "serving_unit" and "serving_qty" are not of correct type
    resp2a = self.client.get(url_for('foods.common_food',food_name='apple',serving_unit='182.00',serving_qty='10.00'))
    resp2b = self.client.get(url_for('foods.common_food',food_name='apple',serving_unit='182.00',serving_qty='not_convertable_to_float'))
    self.assertTrue(resp2a.status_code == 200)
    self.assertTrue(resp2b.status_code == 404)

    # When url parameters serving_unit or serving_qty are None
    resp3 = self.client.get(url_for('foods.common_food',food_name='eggs'))
    self.assertTrue('selected value="50.00"' in resp3.get_data(as_text=True))
    self.assertTrue('value="1.00"' in resp3.get_data(as_text=True))

    # When Form Validates On Submit check redirect
    resp4a = self.client.post(url_for('foods.common_food',food_name='eggs',data = {
      'serving_unit':'50.00',
      'serving_qty':777.00,
      'submit':True
    }),follow_redirects=True)
    resp4b = self.client.post(url_for('foods.common_food',food_name='eggs',data = {
      'serving_unit':'50.00',
      'serving_qty':Decimal(777),
      'submit':True
    }))    
    self.assertTrue(resp4a.status_code==200)
    self.assertTrue(resp4b.status_code==200)

    # Filling in form data when request method is GET
    resp5 = self.client.get(url_for('foods.common_food',food_name='eggs',serving_unit='63.00',serving_qty='999.00'))
    self.assertTrue('selected value="63.00"' in resp5.get_data(as_text=True))
    self.assertTrue('value="999.00"' in resp5.get_data(as_text=True))    

    # Check nutrition updating according to serving_unit and serving_qty
    # (CHECKED AGAINST NUTRITIONIX DATABASE INFORMATION)
    resp6a = self.client.get(url_for('foods.common_food',food_name='eggs',serving_unit='50.00',serving_qty='1.00'))
    resp6b = self.client.get(url_for('foods.common_food',food_name='eggs',serving_unit='50.00',serving_qty='2.00'))
    resp6c = self.client.get(url_for('foods.common_food',food_name='eggs',serving_unit='38.00',serving_qty='1.00'))
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

    # Check 404 response when serving_unit url parameter is not valid to SelectField options
    resp8 = self.client.get(url_for('foods.common_food',food_name='eggs',serving_unit='10.00',serving_qty='1.00'))
    self.assertTrue(resp8.status_code==404)

  def test_foods_branded_food(self):
    big_mac_id = "513fc9e73fe3ffd40300109f"
    fries_id = "513fc9c9673c4fbc26003ff6"
    # Check 404 exception for when food is not in nutritionix database
    resp1a = self.client.get(url_for('foods.branded_food',nix_item_id='asdfasdfas123'))
    resp1b = self.client.get(url_for('foods.branded_food',nix_item_id=big_mac_id))
    self.assertTrue(resp1a.status_code == 404)
    self.assertTrue(resp1b.status_code == 200)

    # Error handling when url parameters "serving_unit" and "serving_qty" are not of correct type
    resp2a = self.client.get(url_for('foods.branded_food',nix_item_id=big_mac_id,serving_unit='212.00',serving_qty='10.00'))
    resp2b = self.client.get(url_for('foods.branded_food',nix_item_id=big_mac_id,serving_unit='212.00',serving_qty='not_convertable_to_float'))
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
    resp4a = self.client.post(url_for('foods.branded_food',nix_item_id=big_mac_id,data = {
      'serving_unit':'212.00',
      'serving_qty':777.00
    }),follow_redirects=True)
    resp4b = self.client.post(url_for('foods.branded_food',nix_item_id=big_mac_id,data = {
      'serving_unit':'212.00',
      'serving_qty':777.00
    }))
    self.assertTrue(resp4a.status_code==200)
    self.assertTrue(resp4b.status_code==200)

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

    # Check 404 response when serving_unit url parameter is not valid to SelectField options
    resp8 = self.client.get(url_for('foods.branded_food',nix_item_id=big_mac_id,serving_unit=1.00,serving_qty=1.00))
    self.assertTrue(resp8.status_code==404)

# test class for 'auth' blueprint
class FlaskAuthTestCase(FlaskClientTestCase):
  def test_auth_register(self):
    # register a new valid account
    response1 = self.client.post(url_for('auth.register'), data = {
      'email':'one@one.com',
      'username':'one',
      'password':'one',
      'password2':'one'
    },follow_redirects=True)
    self.assertEqual(response1.status_code, 200)
    self.assertTrue("Successfully Registered" in response1.get_data(as_text=True))

    # register with empty data
    response2 = self.client.post(url_for('auth.register'), data= {
      'email':"",
      'username':"",
      'password':"",
      'password2':""
    })
    self.assertNotEqual(response2.status_code, 302)

    # register with invalid email
    response3 = self.client.post(url_for('auth.register'), data = {
      'email':'twotwo.com',
      'username':'two',
      'password':'two',
      'password2':'two'
    })
    self.assertNotEqual(response3.status_code, 302)

    # register with invalid username
    response4 = self.client.post(url_for('auth.register'), data = {
      'email':'two@two.com',
      'username':'',
      'password':'two',
      'password2':'two'
    })
    self.assertNotEqual(response4.status_code, 302)    

    # register with unmatching passwords
    response5 = self.client.post(url_for('auth.register'), data = {
      'email':'two@two.com',
      'username':'two',
      'password':'two',
      'password2':'nottwo'
    })
    self.assertNotEqual(response5.status_code, 302)   

    # register with already existing email
    response6 = self.client.post(url_for('auth.register'), data = {
      'email':'one@one.com',
      'username':'two',
      'password':'two',
      'password2':'nottwo'
    })    
    self.assertNotEqual(response6.status_code,302)

    # register with already existing username
    response7 = self.client.post(url_for('auth.register'), data = {
      'email':'two@two.com',
      'username':'one',
      'password':'two',
      'password2':'nottwo'
    })    
    self.assertNotEqual(response7.status_code,302)    


  def test_auth_login_logout(self):
    # invalid email
    response1 = self.client.post(url_for('auth.login'), data= {
      'email':'notanemail',
      'password':'password'
    })
    self.assertNotEqual(response1.status_code,302)

    # invalid password
    response2 = self.client.post(url_for('auth.login'), data= {
      'email':'one@one.com',
      'password':''
    })
    self.assertNotEqual(response2.status_code,302)

    # unsuccessful login
    response8 = self.client.post(url_for('auth.login'), data= {
      'email':'usernotregistered@email.com',
      'password':'password'
    })
    self.assertNotEqual(response8.status_code,302)
    self.assertTrue("Invalid Username or Password" in response8.get_data(as_text=True))

    # successful login
    user = User(email='one@one.com',username='one',password='one')
    db.session.add(user)
    db.session.commit()
    response9 = self.client.post(url_for('auth.login'), data= {
      'email':'one@one.com',
      'password':'one'
    }, follow_redirects=True)
    self.assertEqual(response9.status_code,200)
    self.assertTrue('Logged In Successfully' in response9.get_data(as_text=True))

    # logout
    response10 = self.client.get(url_for('auth.logout'),follow_redirects=True)
    self.assertEqual(response10.status_code,200)
    self.assertTrue('You Have Been Logged Out' in response10.get_data(as_text=True))

# test class for 'carts' blueprint
class FlaskCartsTestCase(unittest.TestCase):
  def setUp(self):
    self.app = create_app('testing')
    self.app_context = self.app.app_context()
    self.app_context.push()
    db.create_all()
    self.client = self.app.test_client(use_cookies=True)

    user = User(email="one@one.com",username="one",password="one")

    # Add carts to user
    cart1 = Cart()
    cart2 = Cart()
    cart3 = Cart()
    cart4 = Cart()
    cart5 = Cart()
    cart1.user = user
    cart2.user = user
    cart3.user = user
    cart4.user = user
    cart5.user = user   

    # Add foods to cart1 and cart2
    food1 = FoodItem(name='food1',
    img_url="",
    nf_calories=Decimal(1),
    nf_total_fat=Decimal(2),
    nf_cholesterol=Decimal(3),
    nf_saturated_fat=Decimal(4),
    nf_sodium=Decimal(5),
    nf_total_carbohydrate=Decimal(6),
    nf_dietary_fiber=Decimal(7),
    nf_sugars=Decimal(8),
    nf_protein=Decimal(9),
    serving_qty=Decimal(1),
    serving_unit="Serving")
    
    food2 = FoodItem(name='food2',
    img_url="",
    nf_calories=Decimal(11),
    nf_total_fat=Decimal(12),
    nf_cholesterol=Decimal(13),
    nf_saturated_fat=Decimal(14),
    nf_sodium=Decimal(15),
    nf_total_carbohydrate=Decimal(16),
    nf_dietary_fiber=Decimal(17),
    nf_sugars=Decimal(18),
    nf_protein=Decimal(19),
    serving_qty=Decimal(1),
    serving_unit="Serving")

    food1.cart = cart1
    food2.cart = cart1
    cart1.update_nutrients()
    cart2.update_nutrients()

    user2 = User(email='two@two.com',username='two',password='two')
    cart6 = Cart()
    cart6.user = user2

    db.session.add_all([user,user2,cart1,cart2,cart3,cart4,cart5,cart6,food1,food2]) 
    db.session.commit()
  
  def tearDown(self):
    db.session.remove()
    db.drop_all()
    self.app_context.pop()

  def test_carts_list(self):
    with self.client:
      self.client.post(url_for('auth.login'), data=
      { 
        'email': 'one@one.com', 
        'username':'one',
        'password': 'one' 
      }
      )

      response1 = self.client.get(url_for('carts.list',username='one'))
      data1 = response1.get_data(as_text=True)
      
      # test that user's carts are shown
      self.assertTrue("Cart 1" in data1)
      self.assertTrue("Cart 2" in data1)
      self.assertTrue("Cart 3" in data1)
      self.assertTrue("Cart 4" in data1)

      # test that only 4 carts are on a page (pagination)
      self.assertFalse("Cart 5" in data1)

      # test that updated cart nutrients are displayed (from added food)
      cart1 = Cart.query.get(1)
      cart1.timestamp = datetime.utcnow()
      db.session.commit()
      response1 = self.client.get(url_for('carts.list',username='one'))
      data1 = response1.get_data(as_text=True)
      self.assertTrue('Calories: 12.00 kcal' in data1)
      self.assertTrue('Total Fat: 14.00 g' in data1)
      self.assertTrue('Saturated Fat: 18.00 g' in data1)
      self.assertTrue('Cholesterol: 16.00 mg' in data1)
      self.assertTrue('Sodium: 20.00 mg' in data1)
      self.assertTrue('Total Carbohydrate: 22.00 g' in data1)
      self.assertTrue('Dietary Fiber: 24.00 g' in data1)
      self.assertTrue('Sugars: 26.00 g' in data1)
      self.assertTrue('Protein: 28.00 g' in data1)

      # test that sorting works (use calories for sorting)
      cart1 = current_user.carts.filter_by(id=1).first()
      cart2 = current_user.carts.filter_by(id=2).first()
      cart3 = current_user.carts.filter_by(id=3).first()
      cart4 = current_user.carts.filter_by(id=4).first()
      cart5 = current_user.carts.filter_by(id=5).first()

      cart1.nf_calories = 1
      cart3.nf_calories = 2
      cart4.nf_calories = 3
      cart5.nf_calories = 4

      # By sorting by calories, cart2 should be excluded from page 1
      # nf_dietary_fiber value of 1000 helps distinguish cart2 from other carts
      cart2.nf_calories = 0
      cart2.nf_dietary_fiber = 1000
      db.session.commit()

      response2 = self.client.get(url_for('carts.list',username='one',nutrient='nf_calories'))
      data2 = response1.get_data(as_text=True)
      self.assertFalse('Dietary Fiber: 1000.00 g' in data2)

      # test 404 error when username is incorrect
      response3 = self.client.get(url_for('carts.list',username='eight'))
      self.assertTrue(response3.status_code == 404)

  def test_carts_followed_carts(self):
    with self.client:
      self.client.post(url_for('auth.login'), data=
      { 
        'email': 'two@two.com', 
        'username':'two',
        'password': 'two' 
      }
      )

      # check that page is blank when current user is not following any other user
      response1 = self.client.get(url_for('carts.followed_carts'))
      data1 = response1.get_data(as_text=True)
      self.assertFalse('Cart 1' in data1)
      self.assertFalse('@one' in data1)

      # check that carts of followed users appear 
      self.client.get(url_for('core.follow',username='one'), follow_redirects=True)
      response2 = self.client.get(url_for('carts.followed_carts'))
      data2 = response2.get_data(as_text=True)
      self.assertTrue('Cart 1' in data2)
      self.assertTrue('Cart 2' in data2)
      self.assertTrue('@one' in data2)


  def test_carts_delete(self):
    with self.client:
      self.client.post(url_for('auth.login'), data=
      { 
        'email': 'one@one.com', 
        'username':'one',
        'password': 'one' 
      }
      )

      self.client.get(url_for('carts.delete',id=5))
      self.client.get(url_for('carts.delete',id=4))

      # test that carts were deleted
      self.assertTrue(len(current_user.carts.all()) == 3)

      # test that aborting works when cart with given id does not exist
      response3 = self.client.get(url_for('carts.delete',id=100))
      self.assertTrue(response3.status_code == 404)

      # test that aborting works when cart does not belong to current user
      response4 = self.client.get(url_for('carts.delete',id=6))
      self.assertTrue(response4.status_code == 403)
  
  def test_carts_add(self):
    with self.client:
      self.client.post(url_for('auth.login'), data=
      { 
        'email': 'one@one.com', 
        'username':'one',
        'password': 'one' 
      }
      )

      self.client.get(url_for('carts.add'))
      self.assertTrue(len(current_user.carts.all()) == 6)

  def test_carts_clone(self):
    with self.client:
      self.client.post(url_for('auth.login'), data=
      { 
        'email': 'two@two.com', 
        'username':'two',
        'password': 'two' 
      }
      )

      # abort if cart does not exist
      response = self.client.get(url_for('carts.clone',id=200))
      self.assertTrue(response.status_code==404)

      # before cloning
      response = self.client.get(url_for('carts.list',username='two'))
      data = response.get_data(as_text=True)
      self.assertTrue('Cart 1' in data)
      self.assertFalse('Cart 2' in data)

      # after cloning
      self.client.get(url_for('carts.clone',id=1),follow_redirects=True)
      response = self.client.get(url_for('carts.list',username='two'))
      data = response.get_data(as_text=True)
      self.assertTrue('Cart 1' in data)
      self.assertTrue('Cart 2' in data)
      self.assertTrue('Calories: 12.00 kcal' in data)
      self.assertTrue('Total Fat: 14.00 g' in data)
      self.assertTrue('Saturated Fat: 18.00 g' in data)
      self.assertTrue('Cholesterol: 16.00 mg' in data)
      self.assertTrue('Sodium: 20.00 mg' in data)
      self.assertTrue('Total Carbohydrate: 22.00 g' in data)
      self.assertTrue('Dietary Fiber: 24.00 g' in data)
      self.assertTrue('Sugars: 26.00 g' in data)
      self.assertTrue('Protein: 28.00 g' in data)

  def test_carts_cart(self):
    with self.client:
      self.client.post(url_for('auth.login'), data=
      { 
        'email': 'one@one.com', 
        'username':'one',
        'password': 'one' 
      }
      )

      response1 = self.client.get(url_for('carts.cart', id=1))
      data1 = response1.get_data(as_text=True)

      self.assertTrue('food1' in data1)
      self.assertTrue('Calories: 1.00 kcal' in data1)
      self.assertTrue('Total Fat: 2.00 g' in data1)
      self.assertTrue('Saturated Fat: 4.00 g' in data1)
      self.assertTrue('Cholesterol: 3.00 mg' in data1)
      self.assertTrue('Sodium: 5.00 mg' in data1)
      self.assertTrue('Total Carbohydrate: 6.00 g' in data1)
      self.assertTrue('Dietary Fiber: 7.00 g' in data1)
      self.assertTrue('Sugars: 8.00 g' in data1)
      self.assertTrue('Protein: 9.00 g' in data1)
      self.assertTrue('Serving Quantity: 1.00' in data1)
      self.assertTrue('Serving Unit: Serving' in data1)

      self.assertTrue('food2' in data1)
      self.assertTrue('Calories: 11.00 kcal' in data1)
      self.assertTrue('Total Fat: 12.00 g' in data1)
      self.assertTrue('Saturated Fat: 14.00 g' in data1)
      self.assertTrue('Cholesterol: 13.00 mg' in data1)
      self.assertTrue('Sodium: 15.00 mg' in data1)
      self.assertTrue('Total Carbohydrate: 16.00 g' in data1)
      self.assertTrue('Dietary Fiber: 17.00 g' in data1)
      self.assertTrue('Sugars: 18.00 g' in data1)
      self.assertTrue('Protein: 19.00 g' in data1)
      self.assertTrue('Serving Quantity: 1.00' in data1)
      self.assertTrue('Serving Unit: Serving' in data1)

      # test that aborting works when cart with given id does not exist 
      response2 = self.client.get(url_for('carts.cart', id=100))
      self.assertTrue(response2.status_code == 404)