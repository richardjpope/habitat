from datetime import timedelta
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
import logging
from celery import Celery
import utils
import os
from habitat import app

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