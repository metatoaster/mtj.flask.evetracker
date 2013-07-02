import os
import unittest
import tempfile

from flask import Flask, session

import mtj.flask.evetracker

from mtj.flask.evetracker import acl
from mtj.flask.evetracker import user


class UserTestCase(unittest.TestCase):

    def setUp(self):
        app = Flask('mtj.flask.evetracker')
        app.config['MTJ_ACL'] = self.auth = acl.SetupAcl('admin', 'password')
        app.config['SECRET_KEY'] = 'test_secret_key'
        app.config['MTJ_LOGGED_IN'] = 'test_logged_in_token'
        app.register_blueprint(user.acl_front, url_prefix='/acl')

        app.config['TESTING'] = True
        self.app = app

    def tearDown(self):
        pass

    def test_login_pass(self):
        with self.app.test_client() as c:
            rv = c.post('/acl/login',
                data={'login': 'admin', 'password': 'password'})
            self.assertEqual(rv.status_code, 302)

    def test_login_fail(self):
        with self.app.test_client() as c:
            rv = c.post('/acl/login',
                data={'login': 'admin', 'password': 'fail'})
            self.assertEqual(rv.status_code, 200)
            self.assertTrue('Invalid credentials' in rv.data)

    def test_user(self):
        with self.app.test_request_context('/'):
            self.assertEqual(user.getCurrentUser(), acl.anonymous)

            # if access token is correctly set.
            session['mtj.user'] = self.auth.generateAccessToken(
                'admin')
            self.assertEqual(user.getCurrentUser().login, 'admin')


if __name__ == '__main__':
    unittest.main()
