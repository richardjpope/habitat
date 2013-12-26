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
   
    from modules.twitter import Twitter
    twitter = Twitter()
    return twitter.settings_view(request)

@app.route("/settings/foursquare", methods=['GET', 'POST'])
def foursquare_settings():
    from modules.foursquare import Foursquare
    foursquare = Foursquare()
    return foursquare.settings_view(request)

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
