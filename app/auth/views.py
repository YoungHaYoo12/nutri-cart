from flask import render_template, redirect, request, url_for, flash
from flask_login import login_user, logout_user, login_required
from app.auth import auth
from app.models import User 
from app.auth.forms import LoginForm

@auth.route('/login', methods=['GET','POST'])
def login():
  form = LoginForm()

  if form.validate_on_submit():
    user = User.query.filter_by(email=form.email.data).first()
    if user is not None and user.verify_password(form.email.password):
      flash('Logged In Successfully')
      login_user(user,form.remember_me.data)
      next = request.args.get('next')
      if next == None or not next[0] == '/':
        next = url_for('core.index')
      return redirect(next)

    flash('Invalid Username or Password')

  return render_template('auth/login.html',form=form)

  @auth.route('/logout')
  @login_required
  def logout():
    logout_user()
    flash('You Have Been Logged Out')
    return redirect(url_for('core.index'))