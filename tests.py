import os
import unittest
import urllib
import urllib2
from client import app as client_app
import mechanize
import threading
import multiprocessing
import time
from habitat import app as server_app

SERVER_URL = 'http://localhost:5000'
CLIENT_URL = 'http://127.0.0.1:8010'

class HabitatTests(unittest.TestCase):

    def setUp(self):

        self.browser = mechanize.Browser()

    def login_server(self):
        self.browser.open(SERVER_URL + '/signin')
        self.browser.form = list(self.browser.forms())[0]
        self.browser['username'] = 'admin'
        self.browser['password'] = 'admin'
        response = self.browser.submit()
        return response.read()

    def logout_server(self):
        response = self.browser.open(SERVER_URL + '/signout')

        return response.read()

    def authorize_client(self):
        response = self.browser.open(CLIENT_URL)
        data = response.read()

        self.browser.form = list(self.browser.forms())[0]
        response = self.browser.submit(nr=0)
        return response.read()

    def test_auth(self):

        data = self.login_server()
        assert 'Sign out' in data

        data = self.authorize_client()
        assert 'oauth_token' in data

    def test_login_logout(self):

        data = self.login_server()
        assert 'Sign out' in data

        data = self.logout_server()
        assert 'Sign in' in data

class MyTests(HabitatTests):
    def test_test(self):
        assert 1 == 1

    def test_test1(self):
        assert 1 == 1


if __name__ == '__main__':
    unittest.main()
