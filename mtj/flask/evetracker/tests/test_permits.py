import os
import unittest

from flask import Flask, Blueprint

from mtj.flask.evetracker import user
from mtj.flask.evetracker.acl import sql
from mtj.flask.evetracker.acl.flask import *


class PermitTestCase(unittest.TestCase):

    def setUp(self):
        app = Flask('mtj.flask.evetracker')
        app.config['MTJ_ACL'] = self.auth = sql.SqlAcl()
        app.config['SECRET_KEY'] = 'test_secret_key'

        app.config['TESTING'] = True

        self.auth.register('testuser', 'password')
        self.auth.addGroup('testgroup')
        testuser = self.auth.getUser('testuser')
        self.auth.setUserGroups(testuser, ('testgroup',))
        self.testgroup = self.auth.getGroup('testgroup')

        @app.before_request
        def check():
            verifyBlueprintPermit()

        self.app = app

        self.test_bp = Blueprint('test_blueprint',
            'mtj.flask.evetracker.test_bp')
        @self.test_bp.route('/test')
        def test():
            return 'Test Success'

        @self.test_bp.route('/restricted')
        @require_permit('__test2')
        def restricted():
            return 'Test Success'

        @self.test_bp.route('/34')
        @require_permit('__test3', '__test4')
        def r34():
            return 'Test Success'

    def tearDown(self):
        # TODO make and call method to reset all the permits
        registerBlueprintPermit(self.test_bp, None)

    def test_blueprint_permit_unregistered(self):
        test_bp = self.test_bp
        self.app.register_blueprint(test_bp, url_prefix='/test_bp')

        with self.app.test_client() as client:
            rv = client.get('/test_bp/test')
            self.assertEqual(rv.data, 'Test Success')

            rv = client.get('/test_bp/restricted')
            self.assertNotEqual(rv.data, 'Test Success')

    def test_blueprint_permit_registered(self):
        test_bp = self.test_bp
        self.app.register_blueprint(test_bp, url_prefix='/test_bp')
        registerBlueprintPermit(test_bp, '__test1')

        with self.app.test_client() as client:
            rv = client.get('/test_bp/test')
            self.assertNotEqual(rv.data, 'Test Success')

            rv = client.get('/test_bp/restricted')
            self.assertNotEqual(rv.data, 'Test Success')

    def test_blueprint_permit_registered_logged_in(self):
        test_bp = self.test_bp
        self.app.register_blueprint(test_bp, url_prefix='/test_bp')
        registerBlueprintPermit(test_bp, '__test1')

        with self.app.test_client() as client:
            with client.session_transaction() as sess:
                sess['mtj.user'] = self.auth.generateAccessToken('testuser')
            rv = client.get('/test_bp/test')
            self.assertNotEqual(rv.data, 'Test Success')

            self.auth.setGroupPermits(self.testgroup, ('__test1',))
            rv = client.get('/test_bp/test')
            self.assertEqual(rv.data, 'Test Success')

            rv = client.get('/test_bp/restricted')
            self.assertNotEqual(rv.data, 'Test Success')

            self.auth.setGroupPermits(self.testgroup, ('__test2',))
            rv = client.get('/test_bp/restricted')
            self.assertNotEqual(rv.data, 'Test Success')

            self.auth.setGroupPermits(self.testgroup, ('__test1', '__test2',))
            rv = client.get('/test_bp/restricted')
            self.assertEqual(rv.data, 'Test Success')

    def test_blueprint_permit_multi_for_view(self):
        test_bp = self.test_bp
        self.app.register_blueprint(test_bp, url_prefix='/test_bp')

        with self.app.test_client() as client:
            with client.session_transaction() as sess:
                sess['mtj.user'] = self.auth.generateAccessToken('testuser')
            rv = client.get('/test_bp/34')
            self.assertNotEqual(rv.data, 'Test Success')

            self.auth.setGroupPermits(self.testgroup, ('__test3',))
            rv = client.get('/test_bp/34')
            self.assertEqual(rv.data, 'Test Success')

            self.auth.setGroupPermits(self.testgroup, ('__test4',))
            rv = client.get('/test_bp/34')
            self.assertEqual(rv.data, 'Test Success')

            self.auth.setGroupPermits(self.testgroup, ('__test3', '__test4',))
            rv = client.get('/test_bp/34')
            self.assertEqual(rv.data, 'Test Success')


# should probably include a test using the app defined at the root.

if __name__ == '__main__':
    unittest.main()
