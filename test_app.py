import urllib
import unittest
import mechanize
import json
import re
from habitat import app, models
from mongoengine import connect
import hashlib
import os

class HabitatTests(unittest.TestCase):

    def setUp(self):

        self.app = app.test_client()

    def tearDown(self):
        mongo_settings =  app.config['MONGODB_SETTINGS']
        db = connect(mongo_settings['DB'])
        db.drop_database(mongo_settings['DB'])

    def random_token(self):
        return  hashlib.sha1(os.urandom(128)).hexdigest()

    def auth_headers(self, access_token):
        return {'Authorization': 'Bearer %s' % access_token, 'Accept': 'application/json'}


    def login(self, username, password):
        return self.app.post('/signin', data=dict(
            username=username,
            password=password
        ), follow_redirects=True)

    def logout(self):
        return self.app.get('/signout', follow_redirects=True)

    def check_add(self, url, data, access_token):
        rv = self.app.post(url,
            data=data,
              headers=self.auth_headers(access_token),
              content_type='application/json'
            )

        assert rv.status == '201 CREATED'
        return rv

    def check_update(self, url, data, access_token):
        rv = self.app.put(url,
            data=data,
              headers=self.auth_headers(access_token),
              content_type='application/json'
            )

        assert rv.status == '200 OK'
        return rv

    def check_view(self, url, test_string, access_token):
        rv = self.app.get(url, headers=self.auth_headers(access_token))
        assert rv.status == '200 OK'
        assert test_string in rv.data

    def check_delete(self, url, access_token):

        rv = self.app.delete(url, headers=self.auth_headers(access_token))
        assert rv.status == '204 NO CONTENT'

        #confirm gone
        rv = self.app.get(url, headers=self.auth_headers(access_token))
        assert rv.status == '404 NOT FOUND'

    def get_access_token(self, scope):

      rv = self.login(app.config['ADMIN_USERNAME'], app.config['ADMIN_PASSWORD'])

      client_id = self.random_token()
      scope = urllib.quote_plus(scope)
      redirect_uri = urllib.quote_plus('http://localhost')
      url = '/oauth/authorize?response_type=token&client_id=%s&scope=%s&redirect_uri=%s' % (client_id, scope, redirect_uri)

      rv = self.app.get(url)

      assert 'permission to' in rv.data

      rv = self.app.post('/oauth/authorize', data=dict(
        client_id=client_id,
        scope=scope,
        response_type='token',
        confirm='yes'),
        follow_redirects=False
      )

      regex = re.compile("access_token=(.*?)&")
      matches = regex.search(rv.location)
      access_token =  matches.groups(1)[0]

      return access_token

    def test_plugins(self):
      
        access_token = self.get_access_token('scenarios')
        rv = self.app.put('/plugins', headers=self.auth_headers(access_token))
        assert rv.status == '200 OK'

    def test_locations(self):

        access_token = self.get_access_token('locations:add locations:view')

        #add location
        data = '{"lnglat": { "type": "Point", "coordinates": [54,0.1] }, "occured_at": "2014-05-15T14:43:48.220Z"}'
        rv = self.check_add('/locations', data, access_token)

        location = json.loads(rv.data)

        #check can view
        self.check_view('/locations', location['id'], access_token)
        self.check_view('/locations/%s' % location['id'], location['id'], access_token)

        #check delete and update not implemented
        rv = self.app.delete('/locations/%s' % location['id'], headers=self.auth_headers(access_token))
        assert rv.status == '405 METHOD NOT ALLOWED'

        rv = self.app.put('/locations/%s' % location['id'], headers=self.auth_headers(access_token))
        assert rv.status == '405 METHOD NOT ALLOWED'


    def test_scenarios(self):

        #get access token
        access_token = self.get_access_token('scenarios')

        #add
        code = '''Feature: Testing
                    Scenario: Near a point in space
                    When I am within 100 meters of "[0,0]"
                    Then ping "http://localhost:5000"'''

        data = json.dumps(dict(code=code))

        rv = self.check_add('/scenarios', data, access_token)
        scenario = json.loads(rv.data)

        #check can view
        self.check_view('/scenarios', scenario['id'], access_token)
        self.check_view('/scenarios/%s' % scenario['id'], scenario['id'], access_token)

        #update
        self.check_update('/scenarios/%s' % scenario['id'], data, access_token)

        #delete
        self.check_delete('/scenarios/%s' % scenario['id'], access_token)

    def test_token_auth(self):

        #make sure we can't call without a token
        rv = self.app.get('/scenarios')
        assert rv.status == '403 FORBIDDEN'

        #do we get a token back?
        access_token = self.get_access_token('scenarios')
        assert access_token

        #is it in the database?
        results = models.AuthToken.objects(access_token=access_token)
        assert len(results) == 1

        #can we make a call with it?
        rv = self.app.get('/scenarios', headers=self.auth_headers(access_token))

        assert rv.status == "200 OK"

    def test_login_logout(self):
        rv = self.login(app.config['ADMIN_USERNAME'], app.config['ADMIN_PASSWORD'])
        assert 'Sign out' in rv.data

        rv = self.logout()
        assert 'Sign in' in rv.data


if __name__ == '__main__':
    unittest.main()
