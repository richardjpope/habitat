import os


DEBUG = True
MONGODB_SETTINGS = {'DB': "openactivity"}
SECRET_KEY = 'fmdnkslr4u8932b3n2'
CELERY_BROKER_URL='mongodb://localhost:27017/openactivity-tasks'
CELERY_RESULT_BACKEND='mongodb://localhost:27017/openactivity-tasks'
CELERY_TIMEZONE = 'Europe/London'
FEATURE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'scenarios')
HABITAT_LOG_FILE = 'habitat.log'

CELERYBEAT_SCHEDULE = {}
