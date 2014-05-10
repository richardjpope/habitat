from flask import render_template, request
from habitat import app, oauth
from models import AuthClient

@app.route('/')
def hello():
    print request.method
    #https://www.flickr.com/photos/54459164@N00/13134244664/
    return render_template('index.html')

@app.route('/oauth/token')
@oauth.token_handler
def access_token():
    return None

@app.route('/oauth/authorize', methods=['GET', 'POST'])
@oauth.authorize_handler
def authorize(*args, **kwargs):

    if request.method == 'GET':
        client_id = kwargs.get('client_id')
        client = AuthClient.objects.get(client_id=client_id)
        kwargs['client'] = client
        return render_template('authorize.html', **kwargs)

    confirm = request.form.get('confirm', 'no')
    return confirm == 'yes'
