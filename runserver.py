import os
import sys

port = int(os.environ.get('PORT', 5000))

#pre flight checks

# check for settings file
if not os.path.isfile('local_config.py'):
    sys.exit("Local config file not found. Run manage.py setup to create one.")

# check for mongo
from mongoengine import connect, ConnectionError
import config
try:
    connect(config.MONGODB_SETTINGS['DB'])
except ConnectionError:
    sys.exit("Unable to connect to mongo database. You may been to start it by running 'mongod'")

if __name__ == '__main__':
    from habitat import app
    app.run(host='0.0.0.0', port=port)
