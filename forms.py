from wtforms import Form, BooleanField, TextField, RadioField, HiddenField, TextAreaField, validators
import foursquare
 
class FoursquareForm(Form):
    client_id = TextField('Client ID', [validators.Required()])
    client_secret = TextField('Client secret', [validators.Required()])

class TwitterForm(Form):
    consumer_key = TextField('Consumer key', [validators.Required()])
    consumer_secret = TextField('Consumer secret', [validators.Required()])