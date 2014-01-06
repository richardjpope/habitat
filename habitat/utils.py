from datetime import timedelta
from flask import Flask
from flask.ext.mongoengine import MongoEngine
import logging
from celery import Celery

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
    'task': 'sources.%s.%s' % (name, function),
    'schedule': timedelta(seconds=seconds)
    }}

    app.config['CELERYBEAT_SCHEDULE'].update(schedule_item)