import os

FEATURE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'habitat/scenarios')
HABITAT_LOG_FILE = 'habitat.log'
CELERYBEAT_SCHEDULE = {}

try:
	from local_config import *
except ImportError:
	print "Local settings file not found. Try creating one. There is an example in local_config.py.git"
	exit()