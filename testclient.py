from flask import Flask, session, request, url_for, jsonify
from flask_oauthlib.client import OAuth
import urllib2
import os
import json

CLIENT_ID = 'GbRmKgbSMmlE2NlugMeFfQIba8hoVyBFsWS8Igsq'
CLIENT_SECRET = 'BfP7jsN8dSsXjGLfTTPiEvarMJOpkZQ2Y7IVVee8X929LfolMV'
ACCESS_TOKEN = ''

app = Flask(__name__)
app.secret_key = 'dsdajdnjskadbhskbddbsajkh'
app.debug = True

oauth_client = OAuth(app)

remote = oauth_client.remote_app(
   'remote',
   consumer_key=CLIENT_ID,
   consumer_secret=CLIENT_SECRET,
   request_token_params={'scope': u'location:add,location:view'},
   base_url='http://localhost:5000',
   request_token_url=None,
   access_token_method='GET',
   access_token_url='http://localhost:5000/oauth/token',
   authorize_url='http://localhost:5000/oauth/authorize'
   )

@app.route('/')
def index():
    if 'remote_oauth' in session:
        return "hello"
        # resp = remote.get('me')
        # return jsonify(resp.data)
        resp = remote.get('locations')

    response = remote.authorize(
        callback='http://127.0.0.1:8010' + url_for('authorized'), _external=True
    )

    return response

@app.route('/call')
def call():
    resp = remote.get('locations')
    return json.dumps(resp.data)

@app.route('/logout')
def logout():
    session.clear()
    return 'done'

@app.route('/authorized')
@remote.authorized_handler
def authorized(resp):
    if resp is None:
        return 'Failed'
    session['remote_oauth'] = (resp['access_token'], '')
    return jsonify(oauth_token=resp['access_token'])

@remote.tokengetter
def get_oauth_token():
    return session.get('remote_oauth')

#
if __name__ == '__main__':
    os.environ['DEBUG'] = 'True'
    app.run(host='0.0.0.0', port=8010)
