from flask_wtf import FlaskForm
from wtforms import DecimalField, SelectField, SubmitField
from wtforms.validators import DataRequired

class FoodServingForm(FlaskForm):
  serving_qty = DecimalField('Serving Quantity',validators=[DataRequired()])
  serving_unit = SelectField('Serving Unit')
  submit = SubmitField('Refresh')