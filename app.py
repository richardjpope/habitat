from flask import Flask, request, redirect, render_template, json, Response, url_for, flash, session, abort
from flask_debugtoolbar import DebugToolbarExtension
from flask.ext.mongoengine import MongoEngine
from mongoengine import connect, DoesNotExist
import datetime
import jinja2
import os
import models
import forms
import re
import os
import glob
import logging
from logging.handlers import RotatingFileHandler

# settings
SCENARIO_DIR = 'testing'
MONGO_URL = os.environ.get("MONGOHQ_URL")
app = Flask(__name__)

#logging
file_handler = logging.handlers.RotatingFileHandler('habitat.log', maxBytes=1024 * 1024 * 100, backupCount=20)
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter('%(asctime)s, %(levelname)s, %(message)s'))
app.logger.setLevel(logging.INFO)
app.logger.addHandler(file_handler)

#database
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
    SCENARIO_DIR = 'scenarios'
)

toolbar = DebugToolbarExtension(app)
db = MongoEngine(app)

# @app.route("/")
# def index():
#     return render_template('index.html')

@app.route("/")
def scenarios():
    scenarios = []
    #from behave import parser
    root_dir = os.path.dirname(os.path.abspath(__file__))
    scenarios_dir = os.path.join(root_dir, app.config['SCENARIO_DIR'])
    for file_name in glob.glob(scenarios_dir + '/*.feature'):
        file_ref = open(file_name)
        contents = file_ref.read()
        scenario_id = os.path.basename(file_name).split('.')[0]
        modified_at = datetime.datetime.fromtimestamp(os.path.getmtime(file_name))
        scenarios.append({'contents': contents, 'modified_at': modified_at, 'scenario_id': scenario_id})
        #scenarios.append(parser.parse_file(file_name).scenarios[0])

    return render_template('scenarios.html', scenarios=scenarios)

@app.route("/scenarios/edit/<scenario_id>", methods=['GET', 'POST'])
def edit(scenario_id):
    form = forms.ScenarioForm(request.form)

    scenario_id = scenario_id.replace('.', '').replace('/', '') #make safe(er) to stop ../../
    root_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(root_dir, app.config['SCENARIO_DIR'], scenario_id) + '.feature'
    if os.path.isfile(file_path):
        file_ref = open(file_path, 'r')
        contents = file_ref.read()
        scenario = {'contents': contents, 'modified_at': None, 'scenario_id': scenario_id}

        if request.method == 'POST' and form.validate():
            file_ref = open(file_path, 'w')
            file_ref.write(form.feature.data)
            return redirect(url_for('scenarios'))

        if request.method == 'GET':
            form.feature.data = scenario['contents']

        return render_template('edit.html', scenario=scenario, form=form)
    else:
        abort(404)

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
