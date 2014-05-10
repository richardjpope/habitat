from flask_oauthlib.provider import OAuth2Provider
from models import AuthClient, AuthGrant, AuthToken
from habitat import oauth
from mongoengine import DoesNotExist
from datetime import datetime, timedelta

scopes = [
  {'scenarios': 'Premission to view, edit and add scenarios'},
  {'location:view': 'Premission to view location history'},
  {'location:add': 'Premission to add to location history'},
]

@oauth.clientgetter
def load_client(client_id):

    try:
      return AuthClient.objects.get(client_id=client_id)
    except DoesNotExist:

      #if doesnt exist, create it
      client = AuthClient()
      client.client_id = client_id
      client.client_secret = 'secret'
      client.name = 'name'
      client._redirect_uris=u'http://127.0.0.1:8001/authorized'
      client.save()

      return client

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

@oauth.tokengetter
def load_token(access_token=None, refresh_token=None):

    if access_token:
        return AuthGrant.get(access_token=access_token)
    elif refresh_token:
        return AuthGrant.get(refresh_token=refresh_token)

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
    # token = token.save()
    # print token
    # print "--------------"
    return token
