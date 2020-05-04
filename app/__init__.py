from config import config 
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app(config_name):
  app = Flask(__name__)
  app.config.from_object(config[config_name])
  config[config_name].init_app(app)

  # Initialize Flask Extension Instances
  db.init_app(app)

  # Register blueprints
  from app.core import core as core_blueprint
  app.register_blueprint(core_blueprint)

  return app