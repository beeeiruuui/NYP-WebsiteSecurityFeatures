from wtforms import Form, StringField, SelectField, TextAreaField, FileField, validators, ValidationError, RadioField, FloatField, IntegerField
from wtforms.fields import EmailField, DateField, DateTimeField, DateTimeLocalField

class usernameforget(Form):
    username = StringField('Username', [validators.DataRequired()])

class otpforget(Form):
    otp = IntegerField('OTP',[validators.number_range(min=1000,max=9999),validators.DataRequired()])

class forgetpassword(Form):
    newpass = StringField('New Password', [validators.DataRequired()])
