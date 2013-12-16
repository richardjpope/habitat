from wtforms import Form, BooleanField, TextField, RadioField, HiddenField, TextAreaField, validators
import foursquare
 
class FoursquareForm(Form):
    client_id = TextField('Client ID', [validators.Required()])
    client_secret = TextField('Client secret', [validators.Required()])

    # def validate_secret(form, field):

    # 	raise validators.ValidationError('Invalid client ID or client secret')
