from flask import Flask, request, redirect, render_template, json, Response, url_for, flash, session, abort
from flask_debugtoolbar import DebugToolbarExtension
from flask.ext.mongoengine import MongoEngine
from mongoengine import connect, DoesNotExist
from datetime import datetime
from celery import Celery
import jinja2
import os
import models
import tasks
import forms
import re
import os
import glob
import logging
import uuid
from logging.handlers import RotatingFileHandler
from behave import parser as behave_parser
from behave import model as behave_models

def make_celery(app):
    celery = Celery('app', broker=app.config['CELERY_BROKER_URL'])
    celery.conf.update(app.config)
    TaskBase = celery.Task
    
    class ContextTask(TaskBase):
        abstract = True
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)
    celery.Task = ContextTask
    return celery

def make_app():

    app = Flask(__name__)
    app.config.from_pyfile('config.py')
    db = MongoEngine(app)

    #logging
    file_handler = logging.handlers.RotatingFileHandler(app.config['HABITAT_LOG_FILE'], maxBytes=1024 * 1024 * 100, backupCount=20)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter('%(asctime)s, %(levelname)s, %(message)s'))
    app.logger.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)

    return app

def make_sources(app, celery):
    from sources.foursquare import Foursquare
    Foursquare(app, celery)

    from sources.twitter import Twitter
    Twitter(app, celery)

app = make_app()
celery = make_celery(app)
make_sources(app, celery)

def generate_file_name(feature):
    from slugify import slugify
    file_name = slugify(feature.name)
    file_name_test = file_name
    is_unique = False
    count = 0
    while not is_unique:
        if not os.path.isfile(os.path.join(app.config['FEATURE_DIR'], file_name_test + '.feature')):
            is_unique = True
        else:
            count = count + 1
            file_name_test = "%s-%s" % (file_name, str(count))

    return file_name_test

def get_feature_file_name(feature_id):
    feature_id = feature_id.replace('.', '').replace('/', '') #make safe(er) to stop ../../     
    return os.path.join(app.config['FEATURE_DIR'], feature_id + '.feature')

def feature_to_string(feature):
    result = "%s: %s \n" % (feature.keyword, feature.name)
    for scenario in feature:
        result = "%s    %s: %s \n" % (result, scenario.keyword, scenario.name)
        for step in scenario.steps:
            result = "%s        %s %s \n" % (result, step.keyword, step.name)
    return result

@celery.task
def run_scenarios():

    from behave.configuration import Configuration, ConfigError
    from behave.runner import Runner
    from behave.runner_util import InvalidFileLocationError, InvalidFilenameError, FileNotFoundError
    from behave.parser import ParserError

    failed = True
    configuration = Configuration(command_args='') # important: without this, the sys.args from celery worker confuse it
    configuration.paths = [app.config['FEATURE_DIR']]
    configuration.format = ['pretty']
    configuration.verbose = True

    app.logger.info('Running scenarios')
    runner = Runner(configuration)

    try:
        failed = runner.run()
    except ParserError, e:
        return "ParseError: %s" % e
    except ConfigError, e:
        return "ConfigError: %s" % e
    except FileNotFoundError, e:
        return "FileNotFoundError: %s" % e
    except InvalidFileLocationError, e:
        return "InvalidFileLocationError: %s" % e
    except InvalidFilenameError, e:
        return "InvalidFilenameError: %s" % e

    return 'worked'

@app.route("/run")
def run_scenarios_view():

    return run_scenarios()

@app.route("/")
def scenarios():

    # result = add_together.delay(23, 45)
    # result.wait()

    features = []
    for feature_file_path in glob.glob(app.config['FEATURE_DIR'] + '/*.feature'):

        feature = behave_parser.parse_file(feature_file_path)
        feature_id = os.path.basename(feature_file_path).split('.')[0]
        modified_at = datetime.fromtimestamp(os.path.getmtime(feature_file_path))

        features.append({'code': feature_to_string(feature), 'modified_at': modified_at, 'feature_id': feature_id})

    return render_template('scenarios.html', features=features)

@app.route("/scenarios/<scenario_id>", methods=['GET', 'POST'])
def edit(scenario_id):

    form = forms.ScenarioForm(request.form)
    if request.method == 'GET':
        if scenario_id != 'new':
            feature_file_path = get_feature_file_name(scenario_id)
            feature = behave_parser.parse_file(feature_file_path)
            form.code.data = feature_to_string(feature)
        else:
            form.code.data = ''

    if request.method == 'POST' and form.validate():
        
        feature = behave_parser.parse_feature(form.code.data)

        feature_file_path = get_feature_file_name(scenario_id)
        if scenario_id == 'new':
            feature_file_path = get_feature_file_name(generate_file_name(feature))

        file_ref = open(feature_file_path, 'w')
        file_ref.write(feature_to_string(feature))
        return redirect(url_for('scenarios'))

    return render_template('edit.html', form=form)

@app.route("/settings")
def settings():
    return render_template('settings.html')

# @app.route("/api/")
# def api():
#     #building: http://localhost:5000/api/?lng=-0.1206612&lat=51.517323
#     #road: http://localhost:5000/api/?lng=-0.120442&lat=51.517546
#     #buildings = models.Fence.objects(polygon__geo_intersects=[float(-0.1206612), float(51.517323)], category='building')
#     buildings = models.Fence.objects(polygon__geo_intersects=[float(request.args.get('lng')), float(request.args.get('lat'))], category='building')
#     print len(buildings)
#     data = {
#         'outside' : len(buildings) == 0
#     }

#     response = Response(json.dumps(data), status=200, mimetype='application/json')
#     return response

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
