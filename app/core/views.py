from flask import render_template
from app.core import core 

@core.route('/')
def index():
  return render_template('main/index.html')