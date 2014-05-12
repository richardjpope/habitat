import json
import unittest
from habitat import app

class TestHabitat(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()

    def login(self, username, password):
        return self.app.post('/signin', data=dict(
            username=username,
            password=password
        ), follow_redirects=True)

    def logout(self):
        return self.app.get('/signout', follow_redirects=True)

    def test_login_logout(self):
        rv = self.login(app.config['ADMIN_USERNAME'], app.config['ADMIN_PASSWORD'])
        print rv.location
        assert 'Hello.' in rv.data
        rv = self.logout()
        assert 'Sign in' in rv.data
        rv = self.login('', '')
        assert 'User name is required' in rv.data
        assert 'Password is required' in rv.data
        rv = self.login("xx%s" % app.config['ADMIN_USERNAME'], "xx%s" % app.config['ADMIN_PASSWORD'])
        assert 'Invalid username or password' in rv.data

    # def test_entry(self):
    #
    #     data = {"id": "530cd73044c01ce9cffa4d9d", "latlng": {"coordinates": [0.32,0.32], "type": "Point"}, "occured_at": "2014-02-24T16:26:11.059000"}
    #     rv = self.app.post('/locations', data=json.dumps(data), content_type='application/json')
    #     self.assertEqual(rv.status_code, 201)

if __name__ == '__main__':
    unittest.main()
