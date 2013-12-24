from flask import Flask, request, redirect, render_template, json, Response, url_for, flash, session
from flask_debugtoolbar import DebugToolbarExtension
from flask.ext.mongoengine import MongoEngine
from mongoengine import connect, DoesNotExist
import jinja2
import os
import models
import forms
import re
import os
import glob

# settings
MONGO_URL = os.environ.get("MONGOHQ_URL")
app = Flask(__name__)

if MONGO_URL:
    credentials = re.sub(r"(.*?)//(.*?)(@hatch)", r"\2",MONGO_URL)
    username = credentials.split(":")[0]
    password = credentials.split(":")[1]
    app.config["MONGODB_DB"] = MONGO_URL.split("/")[-1]
    connect(
        MONGO_URL.split("/")[-1],
        host=MONGO_URL,
        port=1043,
        username=username,
        password=password
    )
app.config.update(
    DEBUG = True,
    MONGODB_SETTINGS = {'DB': "openactivity"},
    SECRET_KEY = 'fmdnkslr4u8932b3n2',
)

toolbar = DebugToolbarExtension(app)
db = MongoEngine(app)

@app.route("/")
def index():
    scenarios = []
    from behave import parser
    root_dir = os.path.dirname(os.path.abspath(__file__))
    scenarios_dir = os.path.join(root_dir, 'scenarios')
    for file_name in glob.glob(scenarios_dir + '/*.feature'):
        # file_ref = open(file_name)
        # scenarios.append(file_ref.read())
        print parser.parse_file(file_name).scenarios[0].steps
        #scenarios.append(parser.parse_file(file_name).scenarios[0])
    return render_template('index.html', scenarios=scenarios)

@app.route("/edit")
def edit():
    return render_template('edit.html')

@app.route("/settings")
def settings():
    return render_template('settings.html')

@app.route("/settings/twitter", methods=['GET', 'POST'])
def twitter_settings():
    
    import tweepy

    form = forms.TwitterForm(request.form)
    try:
        setting = models.Setting.objects.get(key='twitter-auth') # add default
    except DoesNotExist:
        setting = models.Setting()
        setting.key = 'twitter-auth'
        setting.value = {'consumer-key': None, 'consumer-secret':None, 'access-token-key':None, 'access-token-secret':None}

    oauth_token = request.args.get('oauth_token', None)
    oauth_verifier = request.args.get('oauth_verifier', None)
    if request.method == 'GET' and oauth_token and oauth_verifier:
        
        auth = tweepy.OAuthHandler(str(setting.value['consumer-key']), str(setting.value['consumer-secret']))
        request_token = session.get('twitter-request-token', None)
        if request_token:
            session.pop('twitter-request-token')
            auth.set_request_token(request_token[0], request_token[1])
            access_token = auth.get_access_token(oauth_verifier)
            setting.value['access-token-key'] =  access_token.key
            setting.value['access-token-secret'] =  access_token.key
            setting = setting.save()
            flash('Your Twitter account has been linked', 'success')

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
        auth = tweepy.OAuthHandler(str(setting.value['consumer-key']), str(setting.value['consumer-secret']), 'http://127.0.0.1:5000/settings/twitter')
        redirect_url =  auth.get_authorization_url()
        session['twitter-request-token'] = (auth.request_token.key, auth.request_token.secret)
        return redirect(redirect_url)

    return render_template('twitter_settings.html', form=form)

@app.route("/settings/foursquare", methods=['GET', 'POST'])
def foursquare_settings():

    import foursquare

    form = forms.FoursquareForm(request.form)
    try:
        setting = models.Setting.objects.get(key='foursquare-auth') # add default
    except DoesNotExist:
        setting = models.Setting()
        setting.key = 'foursquare-auth'
        setting.value = {'client-id': None, 'client-secret':None, 'access-token':None}

    #check for auth code from foursquare
    access_code = request.args.get('code', None)
    if request.method == 'GET' and access_code:

        client = foursquare.Foursquare(client_id=setting.value['client-id'], client_secret=setting.value['client-secret'], redirect_uri='http://localhost:5000/settings/foursquare')
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
        client = foursquare.Foursquare(client_id=setting.value['client-id'], client_secret=setting.value['client-secret'], redirect_uri='http://localhost:5000/settings/foursquare')
        return redirect(client.oauth.auth_url())

    return render_template('foursquare_settings.html', form=form, setting=setting)

@app.route("/api/")
def api():
    #building: http://localhost:5000/api/?lng=-0.1206612&lat=51.517323
    #road: http://localhost:5000/api/?lng=-0.120442&lat=51.517546
    #buildings = models.Fence.objects(polygon__geo_intersects=[float(-0.1206612), float(51.517323)], category='building')
    buildings = models.Fence.objects(polygon__geo_intersects=[float(request.args.get('lng')), float(request.args.get('lat'))], category='building')
    print len(buildings)
    data = {
        'outside' : len(buildings) == 0
    }

    response = Response(json.dumps(data), status=200, mimetype='application/json')
    return response

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
