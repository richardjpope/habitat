from wtforms import Form, BooleanField, TextField, RadioField, HiddenField, TextAreaField, validators, ValidationError, PasswordField

class AdminLoginForm(Form):
    username = TextField('User name', [validators.Required()])
    password = PasswordField('Password', [validators.Required()])
