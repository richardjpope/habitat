import os
import logging
from flask import Flask
from flask.ext.mongoengine import MongoEngine
from flask.ext import restful
from flask_oauthlib.provider import OAuth2Provider
from flask_restful.utils import cors
from celery import Celery
from logging.handlers import RotatingFileHandler

#app
app = Flask(__name__)
app.config.from_object('config')

#database
db = MongoEngine(app)

#api
api = restful.Api(app)
api.decorators=[cors.crossdomain(origin='*', headers = "origin,content-type,accept,authorization")]

#oauth
oauth = OAuth2Provider(app)

#logging
file_handler = logging.handlers.RotatingFileHandler(app.config['HABITAT_LOG_FILE'], maxBytes=1024 * 1024 * 100, backupCount=20)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(logging.Formatter('%(asctime)s, %(levelname)s, %(message)s'))
app.logger.setLevel(logging.DEBUG)
app.logger.addHandler(file_handler)

#tasks
celery = Celery('app', broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)
TaskBase = celery.Task

class ContextTask(TaskBase):
    abstract = True
    def __call__(self, *args, **kwargs):
        with app.app_context():
            return TaskBase.__call__(self, *args, **kwargs)
celery.Task = ContextTask

from habitat import resources
from habitat import views
from habitat import auth
