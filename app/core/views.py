from flask import render_template, redirect, url_for
from app.core import core 
from app.core.forms import SearchForm

@core.route('/', methods=['GET','POST'])
def index():
  food_form = SearchForm()
  if food_form.validate_on_submit():
    return redirect(url_for('foods.list',food_name=food_form.query.data,filter="common"))

  return render_template('core/index.html',food_form=food_form)