from flask_oauthlib.provider import OAuth2Provider
from models import AuthClient, AuthGrant, AuthToken
from habitat import oauth
from mongoengine import DoesNotExist
from datetime import datetime, timedelta
from functools import wraps
from flask import request

scopes = {'scenarios': 'Permission to view, edit and add scenarios',
  'location:view': 'Permission to view location history',
  'location:add': 'Permission to add to location history',
  'email': 'Permission to add to location history',
}

# a decorator for creating a new client automatically
def pre_authorize_handler(f):

    @wraps(f)
    def decorated(*args, **kwargs):

        if request.method == 'GET' and request.args.get('client_id'):
            try:
                client = AuthClient.objects.get(client_id=request.args.get('client_id'))
            except DoesNotExist:

                client = AuthClient()
                client.client_id = request.args.get('client_id')
                client.client_secret = 'BfP7jsN8dSsXjGLfTTPiEvarMJOpkZQ2Y7IVVee8X929LfolMV'
                client.name = ''
                client._redirect_uris=request.args.get('redirect_uri')
                client.save()

        return f(*args, **kwargs)

    return decorated


@oauth.clientgetter
def load_client(client_id):

    try:
        return AuthClient.objects.get(client_id=client_id)
    except DoesNotExist:
        return None

@oauth.grantgetter
def load_grant(client_id, code):
    try:
      client = AuthClient.objects.get(client_id=client_id)
      grant = AuthGrant.objects(client=client, code=code)[0]
      grant.user = None # OAuth2Provider expects a user
      return grant
    except DoesNotExist:
      return None

@oauth.grantsetter
def save_grant(client_id, code, request, *args, **kwargs):

    client = load_client(client_id)

    expires = datetime.utcnow() + timedelta(seconds=100)
    grant = AuthGrant()
    grant.client = client
    grant.code = code['code']
    grant.redirect_uri=request.redirect_uri
    grant._scopes=' '.join(request.scopes)
    grant.expires=expires

    grant.save()

    return grant

@oauth.usergetter
def get_user(username, password, *args, **kwargs):
    return True

@oauth.tokengetter
def load_token(access_token=None, refresh_token=None):

    if access_token:
        return AuthToken.objects.get(access_token=access_token)
    elif refresh_token:
        return AuthToken.objects.get(refresh_token=refresh_token)

@oauth.tokensetter
def save_token(token_data, request, *args, **kwargs):

    client = load_client(request.client.client_id)

    # make sure that every client has only one token connected to a user
    existing_tokens = AuthToken.objects(client=client)
    for token in existing_tokens:
        token.delete()

    expires_in = token_data.pop('expires_in')
    expires = datetime.utcnow() + timedelta(seconds=expires_in)

    token = AuthToken()
    token.access_token=token_data['access_token']
    token.refresh_token=token_data['refresh_token']
    token.token_type=token_data['token_type']
    token._scopes=token_data['scope']
    token.expires=expires
    token.client = client

    token.save()

    return token
