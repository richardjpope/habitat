from flask import Flask
from flask_debugtoolbar import DebugToolbarExtension
from flask.ext.mongoengine import MongoEngine
from celery import Celery
import os
import logging
import uuid
from logging.handlers import RotatingFileHandler

#app
app = Flask(__name__)
app.config.from_object('config')
db = MongoEngine(app)

#logging
file_handler = logging.handlers.RotatingFileHandler(app.config['HABITAT_LOG_FILE'], maxBytes=1024 * 1024 * 100, backupCount=20)
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter('%(asctime)s, %(levelname)s, %(message)s'))
app.logger.setLevel(logging.INFO)
app.logger.addHandler(file_handler)

#celery
celery = Celery('app', broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)
TaskBase = celery.Task

class ContextTask(TaskBase):
    abstract = True
    def __call__(self, *args, **kwargs):
        with app.app_context():
            return TaskBase.__call__(self, *args, **kwargs)
celery.Task = ContextTask

import habitat.views
import tasks

from sources.foursquare import Foursquare
Foursquare()

from sources.twitter import Twitter
Twitter()