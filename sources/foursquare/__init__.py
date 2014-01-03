from wtforms import Form, TextField, validators
import foursquare as foursquare_api
from mongoengine import DoesNotExist
from flask import request, redirect, flash, session, render_template
import models
from sources import SourceBase

class Foursquare(SourceBase):

	class SettingsForm(Form):
	    client_id = TextField('Client ID', [validators.Required()])
	    client_secret = TextField('Client secret', [validators.Required()])

	def fetch_data(self):
		print "fetching data from foursquare"

	def settings_view(self):

	    form = Foursquare.SettingsForm(request.form)
	    try:
	        setting = models.Setting.objects.get(key='foursquare-auth') # add default
	    except DoesNotExist:
	        setting = models.Setting()
	        setting.key = 'foursquare-auth'
	        setting.value = {'client-id': None, 'client-secret':None, 'access-token':None}

	    #check for auth code from foursquare
	    access_code = request.args.get('code', None)
	    if request.method == 'GET' and access_code:

	        client = foursquare_api.Foursquare(client_id=setting.value['client-id'], client_secret=setting.value['client-secret'], redirect_uri='http://localhost:5000/settings/foursquare')
	        access_token = client.oauth.get_token(access_code)

	        setting.value['access-token'] = access_token
	        setting.save()

	        flash('Your Foursquare account has been linked', 'success')

	    #set initial data
	    if request.method == 'GET' and setting:
	        form.client_id.data = setting.value['client-id']
	        form.client_secret.data = setting.value['client-secret']

	    #save
	    if request.method == 'POST' and form.validate():
	        if not setting:
	            setting = models.Setting()
	        setting.key = 'foursquare-auth'
	        setting.value = {'client-id': form.client_id.data, 'client-secret': form.client_secret.data, 'access-token': setting.value['access-token']}
	        setting = setting.save()

	        #do oauth thing
	        client = foursquare_api.Foursquare(client_id=setting.value['client-id'], client_secret=setting.value['client-secret'], redirect_uri='http://localhost:5000/settings/foursquare')
	        return redirect(client.oauth.auth_url())

	    instructions = ['Visit <a href="https://developer.foursquare.com">developer.foursquare.com</a> and create a new app', "Enter the 'Client ID' and 'Client Secret' for the app in the boxes above.", "Click save and authorise Habitat to access your Foursquare data."]

	    return render_template('setting.html', form=form, setting=setting, instructions=instructions, module_title="Foursquare")