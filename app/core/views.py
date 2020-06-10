from flask import render_template, redirect, url_for
from app.core import core 
from app.core.forms import SearchForm
from app.models import User

@core.route('/', methods=['GET','POST'])
def index():
  form = SearchForm()
  if form.validate_on_submit():
    return redirect(url_for('foods.list',food_name=form.query.data,filter="common"))

  return render_template('core/index.html',form=form)

@core.route('/users/<username>', methods=['GET','POST'])
@core.route('/users', methods=['GET','POST'])
def users(username=None):
  form = SearchForm()
  if form.validate_on_submit():
    return redirect(url_for('core.users', username=form.query.data))

  user = User.query.filter_by(username=username).first()

  return render_template('core/users.html', form=form, query=username,user=user)