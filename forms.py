from wtforms import Form, BooleanField, TextField, RadioField, HiddenField, TextAreaField, validators
 
class TwitterForm(Form):
    consumer_key = TextField('Consumer key', [validators.Required()])
    consumer_secret = TextField('Consumer secret', [validators.Required()])