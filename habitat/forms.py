from wtforms import Form, BooleanField, TextField, RadioField, HiddenField, TextAreaField, validators, ValidationError, PasswordField

class AdminLoginForm(Form):
    username = TextField('User name', [validators.Required(message="User name is required")])
    password = PasswordField('Password', [validators.Required(message="Password is required")])

# class AuthorizeForm(Form):
#     client_name = TextField('Name', [validators.Required()])
