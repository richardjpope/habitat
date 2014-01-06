from wtforms import Form, TextField, validators
import foursquare as foursquare_api
from mongoengine import DoesNotExist
from flask import request, redirect, flash, session, render_template, current_app
import models
import utils
from sources import SourceBase
from datetime import datetime
from celery.task import task

celery = utils.make_celery()

@celery.task
def process_event(self, event):
    print "HELLO"
    print event.id

class Foursquare(SourceBase):

    class SettingsForm(Form):
        client_id = TextField('Client ID', [validators.Required()])
        client_secret = TextField('Client secret', [validators.Required()])

    def register_urls(self, app):
        #app.add_url_rule("/settings/foursquare", 'foursquare_settings', self.settings_view, methods=['GET', 'POST'])
        pass

    def register_tasks(self, celery):
        celery.task(self.fetch_events)
        #celery.task(process_event)

    def schedule_tasks(self, app):
        utils.schedule_reccuring_task(app, 'foursquare', self.fetch_events.__name__, 60)

    # @app.route('/test', methods=['GET', 'POST'])
    def settings_view(self):

        form = Foursquare.SettingsForm(request.form)
        try:
            setting = models.Setting.objects.get(key='foursquare-auth') # add default
        except DoesNotExist:
            setting = models.Setting()
            setting.key = 'foursquare-auth'
            setting.value = {'client-id': None, 'client-secret':None, 'access-token':None}
            print client.users.checkins()

        #check for auth code from foursquare
        access_code = request.args.get('code', None)
        if request.method == 'GET' and access_code:

            client = foursquare_api.Foursquare(client_id=setting.value['client-id'], client_secret=setting.value['client-secret'], redirect_uri='http://localhost:5000/settings/foursquare')
            access_token = client.oauth.get_token(access_code)

            setting.value['access-token'] = access_token
            setting.save()

            flash('Your Foursquare account has been linked', 'success')
            current_app.logger.info('Authorised Foursquare account')

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

    def fetch_events(self):

        print "fetching data from foursquare"
        setting = models.Setting.objects.get(key='foursquare-auth')
        client = foursquare_api.Foursquare(access_token=setting.value['access-token'])
        checkins = client.users.checkins()

        for checkin in checkins['checkins']['items']:
            guid = 'https://foursquare.com/v/%s' % checkin['id']
            event = None
            try:
                event = models.Event.objects.get(guid=guid)
            except DoesNotExist:
                event = models.Event()
                event.guid = guid
                event.data = checkin
                event.source = 'foursquare'
                event.occured_at = datetime.fromtimestamp(checkin['createdAt'])
                event.save()

            # from app import run_scenarios
            # run_scenarios.delay()
            process_event.delay(event)

SourceBase.register(Foursquare)