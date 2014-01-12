import os

FEATURE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'habitat/scenarios')
HABITAT_LOG_FILE = 'habitat.log'
SENDMAIL_PATH = '/usr/sbin/sendmail'
CELERYBEAT_SCHEDULE = {}
EMAIL_FROM = 'alert@habitat'

try:
	from local_config import *
except ImportError:
	print "Local settings file not found. Try creating one. There is an example in local_config.py.git"
	exit()