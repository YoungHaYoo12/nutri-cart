from flask import render_template, redirect, url_for
from app.core import core 
from app.core.forms import SearchForm

@core.route('/', methods=['GET','POST'])
def index():
  form = SearchForm()
  if form.validate_on_submit():
    return redirect(url_for('core.index'))

  return render_template('main/index.html',form=form)