from config import config 
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'


def create_app(config_name):
  app = Flask(__name__)
  app.config.from_object(config[config_name])
  config[config_name].init_app(app)

  # Initialize Flask Extension Instances
  db.init_app(app)
  login_manager.init_app(app)

  # Register blueprints
  from app.core import core as core_blueprint
  from app.foods import foods as foods_blueprint
  from app.errors import errors as errors_blueprint
  from app.auth import auth as auth_blueprint
  from app.carts import carts as carts_blueprint
  
  app.register_blueprint(core_blueprint)
  app.register_blueprint(foods_blueprint)
  app.register_blueprint(errors_blueprint)
  app.register_blueprint(auth_blueprint,url_prefix='/auth')
  app.register_blueprint(carts_blueprint)

  return app