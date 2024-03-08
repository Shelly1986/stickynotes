from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,SubmitField
from wtforms.validators import DataRequired, Email, EqualTo,Length

class RegistrationForm(FlaskForm):
    
    email = StringField('Email',validators=[DataRequired(),Email()])
    password = PasswordField('Password',validators=[DataRequired(),Length(min=6,max=35)])
    confirm_password = PasswordField('Confirm Password',validators=[DataRequired(),EqualTo('password')])
    submit = SubmitField('Sign Up')

class LoginForm(FlaskForm):
    
    email = StringField('Email',validators=[DataRequired(),Email()])
    password = PasswordField('Password',validators=[DataRequired()])
    submit = SubmitField('Login')

class ForgotForm(FlaskForm):
    email = StringField('Email',validators=[DataRequired(),Email()])
    

class VerifyForm(FlaskForm):
    otp = StringField('One Time Password',validators=[DataRequired()])

class ForgotOtp(FlaskForm):
    otp = StringField('One Time Password',validators=[DataRequired()])

class ResetForm(FlaskForm):
    new_password = PasswordField('New Password',validators=[DataRequired(),Length(min=6,max=35)])
    confirm_password = PasswordField('Confirm Password',validators=[DataRequired(),EqualTo('new_password')])
    submit = SubmitField('Reset')