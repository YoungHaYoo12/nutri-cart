from app import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from decimal import Decimal

@login_manager.user_loader
def load_user(user_id):
  return User.query.get(int(user_id))

class User(db.Model, UserMixin):
  __tablename__ = 'users'
  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String(64), unique=True, index=True)
  email = db.Column(db.String(64), unique=True, index=True)
  password_hash = db.Column(db.String(128))
  carts = db.relationship('Cart', backref='user', lazy='dynamic',cascade="all, delete-orphan")

  @property
  def password(self):
    raise AttributeError('password is not a readable attribute')
  
  @password.setter
  def password(self,password):
    self.password_hash = generate_password_hash(password)
  
  def verify_password(self,password):
    return check_password_hash(self.password_hash,password)

  def __repr__(self):
    return f"<User {self.username}>"

class FoodItem(db.Model):
  __tablename__ = 'food_items'

  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(64),index=True)
  nf_calories = db.Column(db.Numeric(decimal_return_scale=2,asdecimal=True))
  nf_total_fat = db.Column(db.Numeric(decimal_return_scale=2,asdecimal=True))
  nf_saturated_fat = db.Column(db.Numeric(decimal_return_scale=2,asdecimal=True))
  nf_cholesterol = db.Column(db.Numeric(decimal_return_scale=2,asdecimal=True))
  nf_sodium = db.Column(db.Numeric(decimal_return_scale=2,asdecimal=True))
  nf_total_carbohydrate = db.Column(db.Numeric(decimal_return_scale=2,asdecimal=True))
  nf_dietary_fiber = db.Column(db.Numeric(decimal_return_scale=2,asdecimal=True))
  nf_sugars = db.Column(db.Numeric(decimal_return_scale=2,asdecimal=True))
  nf_protein = db.Column(db.Numeric(decimal_return_scale=2,asdecimal=True))
  nutrient_multiplier = db.Column(db.Numeric(decimal_return_scale=2,asdecimal=True))
  serving_qty = db.Column(db.Numeric(decimal_return_scale=2,asdecimal=True))
  serving_unit = db.Column(db.String(32))

  cart_id = db.Column(db.Integer, db.ForeignKey('carts.id'))

  def __init__(self,name,nf_calories=None,nf_total_fat=None,nf_saturated_fat=None,nf_cholesterol=None,nf_sodium=None,nf_total_carbohydrate=None,nf_dietary_fiber=None,nf_sugars=None,nf_protein=None,nutrient_multiplier=None, serving_qty=None, serving_unit=None):
    if nutrient_multiplier is None:
      nutrient_multiplier = Decimal(1)
    
    self.name = name
    self.nf_calories = nf_calories * nutrient_multiplier or Decimal(0)
    self.nf_total_fat = nf_total_fat * nutrient_multiplier or Decimal(0)
    self.nf_saturated_fat = nf_saturated_fat * nutrient_multiplier or Decimal(0)
    self.nf_cholesterol = nf_cholesterol * nutrient_multiplier or Decimal(0)
    self.nf_sodium = nf_sodium * nutrient_multiplier or Decimal(0)
    self.nf_total_carbohydrate = nf_total_carbohydrate * nutrient_multiplier or Decimal(0)
    self.nf_dietary_fiber = nf_dietary_fiber * nutrient_multiplier or Decimal(0)
    self.nf_sugars = nf_sugars * nutrient_multiplier or Decimal(0)
    self.nf_protein = nf_protein * nutrient_multiplier or Decimal(0)
    self.nutrient_multiplier = nutrient_multiplier
    self.serving_qty = serving_qty or Decimal(0)
    self.serving_unit = serving_unit or Decimal(0)
  
  def __repr__(self):
    return f"{self.name} in {self.cart}"

class Cart(db.Model):
  __tablename__ = 'carts'

  id = db.Column(db.Integer, primary_key=True)
  cart_num = db.Column(db.Integer)
  foods = db.relationship('FoodItem', backref='cart', cascade="all, delete-orphan")
  user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

  nf_calories = db.Column(db.Numeric(asdecimal=True,decimal_return_scale=2))
  nf_total_fat = db.Column(db.Numeric(asdecimal=True,decimal_return_scale=2))
  nf_saturated_fat = db.Column(db.Numeric(asdecimal=True,decimal_return_scale=2))
  nf_cholesterol = db.Column(db.Numeric(asdecimal=True,decimal_return_scale=2))
  nf_sodium = db.Column(db.Numeric(asdecimal=True,decimal_return_scale=2))
  nf_total_carbohydrate = db.Column(db.Numeric(asdecimal=True,decimal_return_scale=2))
  nf_dietary_fiber = db.Column(db.Numeric(asdecimal=True,decimal_return_scale=2))
  nf_sugars = db.Column(db.Numeric(asdecimal=True,decimal_return_scale=2))
  nf_protein = db.Column(db.Numeric(asdecimal=True,decimal_return_scale=2))

  # update total nutrients 
  def update_nutrients(self):
    nf_calories_sum = 0
    nf_total_fat_sum = 0
    nf_saturated_fat_sum = 0
    nf_cholesterol_sum = 0
    nf_sodium_sum = 0
    nf_total_carbohydrate_sum = 0
    nf_dietary_fiber_sum = 0
    nf_sugars_sum = 0
    nf_protein_sum = 0

    for food in self.foods:
      nf_calories_sum += food.nf_calories
      nf_total_fat_sum += food.nf_total_fat
      nf_saturated_fat_sum += food.nf_saturated_fat
      nf_cholesterol_sum += food.nf_cholesterol
      nf_sodium_sum += food.nf_sodium
      nf_total_carbohydrate_sum += food.nf_total_carbohydrate
      nf_dietary_fiber_sum += food.nf_dietary_fiber
      nf_sugars_sum += food.nf_sugars
      nf_protein_sum += food.nf_protein
    
    self.nf_calories = nf_calories_sum
    self.nf_total_fat = nf_total_fat_sum
    self.nf_saturated_fat = nf_saturated_fat_sum
    self.nf_cholesterol = nf_cholesterol_sum
    self.nf_sodium = nf_sodium_sum
    self.nf_total_carbohydrate = nf_total_carbohydrate_sum
    self.nf_dietary_fiber = nf_dietary_fiber_sum
    self.nf_sugars = nf_sugars_sum
    self.nf_protein = nf_protein_sum

  def __init__(self, cart_num):
    self.cart_num = cart_num
    self.nf_calories = Decimal(0)
    self.nf_total_fat = Decimal(0)
    self.nf_saturated_fat = Decimal(0)
    self.nf_cholesterol = Decimal(0)
    self.nf_sodium = Decimal(0)
    self.nf_total_carbohydrate = Decimal(0)
    self.nf_dietary_fiber = Decimal(0)
    self.nf_sugars = Decimal(0)
    self.nf_protein = Decimal(0)

  def __repr__(self):
    return f"Cart {self.cart_num} of {self.user}"