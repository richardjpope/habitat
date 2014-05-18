import os
import sys

port = int(os.environ.get('PORT', 5000))

#pre flight checks

# - check for mongo
from mongoengine import connect, ConnectionError
import config
try:
    connect(config.MONGODB_SETTINGS['DB'])
except ConnectionError:
    sys.exit("Unable to connect to database")

if __name__ == '__main__':
    from habitat import app
    app.run(host='0.0.0.0', port=port)
