from wtforms import Form, BooleanField, TextField, RadioField, HiddenField, TextAreaField, validators, ValidationError
from behave.parser import parse_feature, ParserError

class ScenarioForm(Form):
    code = TextAreaField('Code', [validators.Required()])

    def validate_code(form, field):
		try:
			parse_feature(field.data)
		except ParserError:
			raise ValidationError('Feature is not valid')