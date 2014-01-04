from wtforms import Form, TextField, validators
import tweepy as twitter_api
from mongoengine import DoesNotExist
from flask import request, redirect, flash, session, render_template, current_app
import models
from sources import SourceBase

class Twitter(SourceBase):

    class SettingsForm(Form):
        consumer_key = TextField('Consumer key', [validators.Required()])
        consumer_secret = TextField('Consumer secret', [validators.Required()])        

    def fetch_data(self):
        print "fetching data from twitter"


    def settings_view(self):
        form = Twitter.SettingsForm(request.form)
        try:
            setting = models.Setting.objects.get(key='twitter-auth') # add default
        except DoesNotExist:
            setting = models.Setting()
            setting.key = 'twitter-auth'
            setting.value = {'consumer-key': None, 'consumer-secret':None, 'access-token-key':None, 'access-token-secret':None}

        oauth_token = request.args.get('oauth_token', None)
        oauth_verifier = request.args.get('oauth_verifier', None)
        if request.method == 'GET' and oauth_token and oauth_verifier:
            
            auth = twitter_api.OAuthHandler(str(setting.value['consumer-key']), str(setting.value['consumer-secret']))
            request_token = session.get('twitter-request-token', None)
            if request_token:
                session.pop('twitter-request-token')
                auth.set_request_token(request_token[0], request_token[1])
                access_token = auth.get_access_token(oauth_verifier)
                setting.value['access-token-key'] =  access_token.key
                setting.value['access-token-secret'] =  access_token.key
                setting = setting.save()

                #get the username for authenticated account (mainly for logging purposes)
                client = twitter_api.API(auth)
                screen_name = client.me().screen_name
                flash('The twitter account for %s has been added to Habitat' % screen_name, 'success')
                current_app.logger.info('Authorised Twitter account %s ' % screen_name)

        #set initial data
        if request.method == 'GET' and setting:
            form.consumer_key.data = setting.value['consumer-key']
            form.consumer_secret.data = setting.value['consumer-secret']

        #save
        if request.method == 'POST' and form.validate():
            if not setting:
                setting = models.Setting()
            setting.key = 'twitter-auth'
            setting.value = {'consumer-key': form.consumer_key.data, 'consumer-secret': form.consumer_secret.data, 'access-token-key': setting.value['access-token-key'], 'access-token-secret': setting.value['access-token-secret']}
            setting = setting.save()

            #do oauth thing
            auth = twitter_api.OAuthHandler(str(setting.value['consumer-key']), str(setting.value['consumer-secret']), 'http://127.0.0.1:5000/settings/twitter')
            redirect_url =  auth.get_authorization_url()
            session['twitter-request-token'] = (auth.request_token.key, auth.request_token.secret)
            return redirect(redirect_url)


        instructions = ['Visit <a href="https://dev.twitter.com/apps/new">dev.twitter.com</a> and create a new app. Enter any valid url in the \'website\' box.', 'Set the \'Callback URL\' to the URL of this page', 'Enter the \'Consumer ID\' and \'Consumer secret\' for the app in the boxes above', 'Click save and authorise Habitat to access your Twitter data.']

        return render_template('setting.html', form=form, setting=setting, instructions=instructions, module_title="Twitter")