import unittest
from sqlalchemy.exc import IntegrityError
from app import create_app, db
from app.models import User,FoodItem,Cart
from decimal import Decimal

class FlaskTestCase(unittest.TestCase):
  def setUp(self):
    self.app = create_app('testing')
    self.app_context = self.app.app_context()
    self.app_context.push()
    db.create_all()

  def tearDown(self):
    db.session.remove()
    db.drop_all()
    self.app_context.pop()

class UserModelTestCase(FlaskTestCase):
  def test_password_setter(self):
    u = User(password='one')
    self.assertTrue(u.password_hash is not None)
  
  def test_no_password_getter(self):
    u = User(password='one')
    with self.assertRaises(AttributeError):
      u.password
  
  def test_password_verification(self):
    u = User(password='one')
    self.assertTrue(u.verify_password('one'))
    self.assertFalse(u.verify_password('two'))
  
  def test_password_salts_are_random(self):
    u1 = User(password='one')
    u2 = User(password='one')
    self.assertTrue(u1.password_hash != u2.password_hash)

  def test_email_username_id_repr_tablename(self):
    u1 = User(email='test@test.com',username='test',password='test')
    db.session.add(u1)
    db.session.commit()

    self.assertEqual(u1.email,'test@test.com')
    self.assertEqual(u1.username,'test')
    self.assertEqual(u1.id,1)
    self.assertEqual(u1.__repr__(),'<User test>')
    self.assertEqual(u1.__tablename__, 'users')

  
  def test_non_unique_email(self):
    u1 = User(email='one@one.com', username='one', password='one')
    u2 = User(email='one@one.com',username='two',password='two')

    db.session.add(u1)
    db.session.commit()

    with self.assertRaises(IntegrityError):
      db.session.add(u2)
      db.session.commit()

  def test_non_unique_username(self):
    u1 = User(email='one@one.com', username='one', password='one')
    u2 = User(email='two@two.com',username='one',password='two')

    db.session.add(u1)
    db.session.commit()

    with self.assertRaises(IntegrityError):
      db.session.add(u2)
      db.session.commit()

class FoodItemModelTestCase(FlaskTestCase):
  def test_decimal_fields(self):
    name = 'food1'
    nf_calories = Decimal(1.00)
    nf_total_fat = Decimal(2.00)
    nf_cholesterol = Decimal(3.00)
    nf_saturated_fat = Decimal(4.00)
    nf_sodium = Decimal(5.00)
    nf_total_carbohydrate = Decimal(6.00)
    nf_dietary_fiber = Decimal(7.00)
    nf_sugars = Decimal(8.00)
    nf_protein = Decimal(9.00)
    serving_qty = Decimal(10.00)
    serving_unit='serving'
    nutrient_multiplier = Decimal(2.00)

    food1 = FoodItem(name=name,
    nf_calories=nf_calories,
    nf_total_fat=nf_total_fat,
    nf_cholesterol=nf_cholesterol,
    nf_saturated_fat=nf_saturated_fat,
    nf_sodium=nf_sodium,
    nf_total_carbohydrate=nf_total_carbohydrate,
    nf_dietary_fiber=nf_dietary_fiber,
    nf_sugars=nf_sugars,
    nf_protein=nf_protein,
    serving_qty=serving_qty,
    serving_unit=serving_unit,
    nutrient_multiplier=nutrient_multiplier
    )

    # check type decimal
    self.assertTrue(type(food1.nf_calories) == Decimal)
    self.assertTrue(type(food1.nf_total_fat) == Decimal)
    self.assertTrue(type(food1.nf_cholesterol) == Decimal)
    self.assertTrue(type(food1.nf_saturated_fat) == Decimal)
    self.assertTrue(type(food1.nf_sodium) == Decimal)
    self.assertTrue(type(food1.nf_total_carbohydrate) == Decimal)
    self.assertTrue(type(food1.nf_dietary_fiber) == Decimal)
    self.assertTrue(type(food1.nf_sugars) == Decimal)
    self.assertTrue(type(food1.nf_protein) == Decimal)
    self.assertTrue(type(food1.serving_qty) == Decimal)

    # check whether nutrient_multiplier is multiplied to nutrients
    self.assertTrue(food1.nf_calories == Decimal(2))
    self.assertTrue(food1.nf_total_fat == Decimal(4))
    self.assertTrue(food1.nf_cholesterol == Decimal(6))
    self.assertTrue(food1.nf_saturated_fat == Decimal(8))
    self.assertTrue(food1.nf_sodium == Decimal(10))
    self.assertTrue(food1.nf_total_carbohydrate == Decimal(12))
    self.assertTrue(food1.nf_dietary_fiber == Decimal(14))
    self.assertTrue(food1.nf_sugars == Decimal(16))
    self.assertTrue(food1.nf_protein == Decimal(18))

    # check default value of nutrient_multiplier 
    name = 'food2'
    food2 = FoodItem(name=name,
    nf_calories=nf_calories,
    nf_total_fat=nf_total_fat,
    nf_cholesterol=nf_cholesterol,
    nf_saturated_fat=nf_saturated_fat,
    nf_sodium=nf_sodium,
    nf_total_carbohydrate=nf_total_carbohydrate,
    nf_dietary_fiber=nf_dietary_fiber,
    nf_sugars=nf_sugars,
    nf_protein=nf_protein,
    serving_qty=serving_qty,
    serving_unit=serving_unit,
    )    
    self.assertTrue(food2.nutrient_multiplier == Decimal(1))
    self.assertTrue(food2.nf_calories == Decimal(1))
    self.assertTrue(food2.nf_total_fat == Decimal(2))
    self.assertTrue(food2.nf_cholesterol == Decimal(3))
    self.assertTrue(food2.nf_saturated_fat == Decimal(4))
    self.assertTrue(food2.nf_sodium == Decimal(5))
    self.assertTrue(food2.nf_total_carbohydrate == Decimal(6))
    self.assertTrue(food2.nf_dietary_fiber == Decimal(7))
    self.assertTrue(food2.nf_sugars == Decimal(8))
    self.assertTrue(food2.nf_protein == Decimal(9))

class CartModelTestCase(FlaskTestCase):
  def test_default_values(self):
    cart1 = Cart()

    # test initial values given to Cart fields 
    self.assertTrue(cart1.nf_calories == Decimal(0))
    self.assertTrue(cart1.nf_total_fat == Decimal(0))
    self.assertTrue(cart1.nf_saturated_fat == Decimal(0))
    self.assertTrue(cart1.nf_cholesterol == Decimal(0))
    self.assertTrue(cart1.nf_sodium == Decimal(0))
    self.assertTrue(cart1.nf_total_carbohydrate == Decimal(0))
    self.assertTrue(cart1.nf_dietary_fiber == Decimal(0))
    self.assertTrue(cart1.nf_sugars == Decimal(0))
    self.assertTrue(cart1.nf_protein == Decimal(0))
  
  def test_update_nutrients(self):
    food1 = FoodItem(name='food1',
    nf_calories=Decimal(1),
    nf_total_fat=Decimal(2),
    nf_cholesterol=Decimal(3),
    nf_saturated_fat=Decimal(4),
    nf_sodium=Decimal(5),
    nf_total_carbohydrate=Decimal(6),
    nf_dietary_fiber=Decimal(7),
    nf_sugars=Decimal(8),
    nf_protein=Decimal(9),
    nutrient_multiplier=Decimal(1))

    food2 = FoodItem(name='food2',
    nf_calories=Decimal(11),
    nf_total_fat=Decimal(12),
    nf_cholesterol=Decimal(13),
    nf_saturated_fat=Decimal(14),
    nf_sodium=Decimal(15),
    nf_total_carbohydrate=Decimal(16),
    nf_dietary_fiber=Decimal(17),
    nf_sugars=Decimal(18),
    nf_protein=Decimal(19),
    nutrient_multiplier=Decimal(1))

    cart2 = Cart()
    food1.cart = cart2
    food2.cart = cart2

    cart2.update_nutrients()
    self.assertTrue(cart2.nf_calories == Decimal(12))
    self.assertTrue(cart2.nf_total_fat == Decimal(14))
    self.assertTrue(cart2.nf_cholesterol == Decimal(16))
    self.assertTrue(cart2.nf_saturated_fat == Decimal(18))
    self.assertTrue(cart2.nf_sodium == Decimal(20))
    self.assertTrue(cart2.nf_total_carbohydrate == Decimal(22))
    self.assertTrue(cart2.nf_dietary_fiber == Decimal(24))
    self.assertTrue(cart2.nf_sugars == Decimal(26))
    self.assertTrue(cart2.nf_protein == Decimal(28))
  
  def test_relationships(self):
    food1 = FoodItem(name='food1',
    nf_calories=Decimal(1),
    nf_total_fat=Decimal(2),
    nf_cholesterol=Decimal(3),
    nf_saturated_fat=Decimal(4),
    nf_sodium=Decimal(5),
    nf_total_carbohydrate=Decimal(6),
    nf_dietary_fiber=Decimal(7),
    nf_sugars=Decimal(8),
    nf_protein=Decimal(9),
    nutrient_multiplier=Decimal(1))

    food2 = FoodItem(name='food2',
    nf_calories=Decimal(11),
    nf_total_fat=Decimal(12),
    nf_cholesterol=Decimal(13),
    nf_saturated_fat=Decimal(14),
    nf_sodium=Decimal(15),
    nf_total_carbohydrate=Decimal(16),
    nf_dietary_fiber=Decimal(17),
    nf_sugars=Decimal(18),
    nf_protein=Decimal(19),
    nutrient_multiplier=Decimal(1))

    cart1 = Cart()
    cart2 = Cart()

    user1 = User(email="one@one.com",username="one",password="one")
    user2 = User(email="two@two.com",username="two",password="two")

    food1.cart = cart1
    cart1.user = user1
    food2.cart = cart2
    cart2.user = user2

    # check relationships
    self.assertTrue(food1.cart == cart1)
    self.assertTrue(cart1.user == user1)
    self.assertTrue(food2.cart == cart2)
    self.assertTrue(cart2.user == user2)

    # test relationships are showed in __repr__
    self.assertTrue(food1.__repr__() == 'food1 in Cart of <User one>')
    self.assertTrue(cart1.__repr__() == 'Cart of <User one>')
    self.assertTrue(user1.__repr__() == '<User one>')
