from datetime import timedelta
from flask import Flask
from flask.ext.mongoengine import MongoEngine
import logging
from celery import Celery
import utils
import os
from habitat import app

def make_celery():

    #todo: should not have to create an app just to read the config
    app = Flask(__name__)
    app.config.from_pyfile('config.py')

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

def schedule_reccuring_task(app, name, function, seconds):
    schedule_item = {'fetch-data-%s' % name: {
    'task': 'habitat.sources.%s.%s' % (name, function),
    'schedule': timedelta(seconds=seconds)
    }}

    app.config['CELERYBEAT_SCHEDULE'].update(schedule_item)

def generate_feature_file_name(feature):
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