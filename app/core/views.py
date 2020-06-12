from flask import render_template, redirect, url_for,flash
from flask_login import login_required,current_user
from app import db
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

@core.route('/follow/<username>')
@login_required
def follow(username):
  user = User.query.filter_by(username=username).first()
  if user is None:
    flash('Invalid User')
    return redirect(url_for('core.index'))
  if current_user.is_following(user):
    flash('You are already following this user.')
    return redirect(url_for('carts.list',username=username))
  current_user.follow(user)
  db.session.commit()
  flash(f"You are now following {username}")
  return redirect(url_for('carts.list',username=username))

@core.route('/unfollow/<username>')
@login_required
def unfollow(username):
  user = User.query.filter_by(username=username).first()
  if user is None:
    flash('Invalid User')
    return redirect(url_for('core.index'))
  if not current_user.is_following(user):
    flash('You are currently not following this user.')
    return redirect(url_for('carts.list',username=username))
  current_user.unfollow(user)
  db.session.commit()
  flash(f"You are no longer following {username}")
  return redirect(url_for('carts.list',username=username))