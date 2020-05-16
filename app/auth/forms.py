from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo
from wtforms import ValidationError
from app.models import User

class LoginForm(FlaskForm):
  email = StringField('Email', validators=[DataRequired(), Email(), Length(1,64)])
  password = PasswordField('Password', validators=[DataRequired()])
  remember_me = BooleanField('Keep Me Logged In')
  submit = SubmitField('Log In')

class RegistrationForm(FlaskForm):
  email = StringField('Email', validators=[DataRequired(), Length(1,64), Email()])
  username = StringField('Username', validators=[DataRequired(), Length(1,64)])
  password = PasswordField('Password', validators=[DataRequired(), EqualTo('password2', message='Passwords Must Match')])
  password2 = PasswordField('Confirm Password', validators=[DataRequired()])
  submit = SubmitField('Register')

  def validate_email(self, field):
    if User.query.filter_by(email=field.data).first():
      raise ValidationError('Email Already Registered')
  
  def validate_username(self, field):
    if User.query.filter_by(username=field.data).first():
      raise ValidationError('Username Already In Use')