from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

class SearchForm(FlaskForm):
  query = StringField('Query',validators=[DataRequired(message="Query Field Empty")])
  submit = SubmitField('Search')