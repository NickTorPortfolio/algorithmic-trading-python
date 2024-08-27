from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, DateField, SubmitField
from wtforms.validators import DataRequired, Length, Email, EqualTo, Regexp

class RegistrationForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Regexp(r"^[a-zA-Z\s'-]+$")])
    surname = StringField('Surname', validators=[DataRequired(), Regexp(r"^[a-zA-Z\s'-]+$")])
    date_of_birth = DateField('Date of Birth', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    username = StringField('Username', validators=[DataRequired(), Regexp(r"^\w+$")])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=8),
        Regexp(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[\W_]).+$')
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match')
    ])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class RecoveryForm(FlaskForm):
    # Define form fields for account recovery
    pass

class AutoTradingForm(FlaskForm):
    symbol = StringField('Stock Symbol', validators=[DataRequired(), Regexp(r"^[A-Za-z0-9_]+$")])
    percentage_threshold = IntegerField('Percentage Threshold of Initial Capital', validators=[DataRequired(), NumberRange(min=1, max=100)])
    submit = SubmitField('Start Auto-Trading')