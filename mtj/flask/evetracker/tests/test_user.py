import os
import unittest
import tempfile

from flask import Flask, session
from werkzeug.exceptions import Forbidden

import mtj.flask.evetracker

from mtj.flask.evetracker import acl
from mtj.flask.evetracker import user


class UserTestCase(unittest.TestCase):

    def setUp(self):
        app = Flask('mtj.flask.evetracker')
        app.config['MTJ_ACL'] = self.auth = acl.SetupAcl('user', 'password')
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
        # simple test
        with self.app.test_request_context('/'):
            self.assertEqual(user.getCurrentUser(), acl.anonymous)

            # if access token is correctly set.
            session['mtj.user'] = self.auth.generateAccessToken('admin')
            self.assertEqual(user.getCurrentUser().login, 'admin')

    def test_group(self):
        # simple test
        with self.app.test_request_context('/'):
            session['mtj.user'] = self.auth.generateAccessToken('admin')
            self.assertTrue(user.verifyUserGroupByName('admin'))
            self.assertRaises(Forbidden,
                user.verifyUserGroupByName, 'fakegroup')

            session['mtj.user'] = self.auth.generateAccessToken('user')
            self.assertRaises(Forbidden,
                user.verifyUserGroupByName, 'admin')

    def test_list_user(self):
        with self.app.test_client() as c:
            rv = c.get('/acl/list')
            self.assertFalse('<td>admin</td>' in rv.data)

            rv = c.post('/acl/login',
                data={'login': 'admin', 'password': 'password'})
            rv = c.get('/acl/list')
            self.assertTrue('<td>admin</td>' in rv.data)

    def test_current_user_options(self):
        with self.app.test_client() as c:
            rv = c.post('/acl/login',
                data={'login': 'admin', 'password': 'password'})
            rv = c.get('/acl/current')
            self.assertTrue('<a href="add">' in rv.data)
            self.assertTrue('<a href="list">' in rv.data)

            rv = c.post('/acl/logout')
            rv = c.post('/acl/login',
                data={'login': 'user', 'password': 'password'})
            rv = c.get('/acl/current')
            self.assertFalse('<a href="add">' in rv.data)
            self.assertFalse('<a href="list">' in rv.data)

    def test_edit_user(self):
        with self.app.test_client() as c:
            rv = c.post('/acl/login',
                data={'login': 'admin', 'password': 'password'})
            rv = c.get('/acl/edit/admin')
            self.assertTrue('value="admin">' in rv.data)
            rv = c.get('/acl/edit/nouser')
            self.assertTrue('<h1>Not Found</h1>' in rv.data)

    def test_passwd(self):
        with self.app.test_client() as c:
            rv = c.post('/acl/login',
                data={'login': 'admin', 'password': 'password'})

            rv = c.post('/acl/passwd')
            self.assertTrue('Please fill out all the required fields.'
                in rv.data)

            rv = c.post('/acl/passwd', data={
                'old_password': 'fail', 'password': 'newpassword',
                'confirm_password': 'failure'})
            self.assertTrue('Old password incorrect' in rv.data)

            rv = c.post('/acl/passwd', data={
                'old_password': 'password', 'password': 'newpassword',
                'confirm_password': 'failure'})
            self.assertTrue('Password and confirmation password mismatched.'
                in rv.data)

            rv = c.post('/acl/passwd', data={
                'old_password': 'password', 'password': '1',
                'confirm_password': '1'})
            self.assertTrue('New password too short.' in rv.data)

            rv = c.post('/acl/passwd', data={
                'old_password': 'password', 'password': '123456',
                'confirm_password': '123456'})
            self.assertTrue('Error updating password.' in rv.data)


if __name__ == '__main__':
    unittest.main()
