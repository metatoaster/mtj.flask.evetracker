from unittest import TestCase, TestSuite, makeSuite
from flask import Flask, session, request
from werkzeug.exceptions import Forbidden

from mtj.flask.evetracker.hooks import check_backdoor
from mtj.eve.tracker.frontend.flask import json_frontend


class BackdoorTestCase(TestCase):
    """
    Test the intergration of the protection into the core app.
    """

    def setUp(self):
        self.app = Flask('mtj.flask.evetracker')
        self.app.config['SECRET_KEY'] = 'test_secret_key'
        self.app.config['MTJ_BACKDOOR'] = 'backdoor'
        self.app.register_blueprint(json_frontend, url_prefix='/json')

    def tearDown(self):
        pass

    def test_backdoor_default(self):
        with self.app.test_request_context('/'):
            self.assertFalse(check_backdoor())

        with self.app.test_request_context('/',
                headers={'Authorization': 'Backdoor backdoor'}):
            self.assertTrue(check_backdoor())

    def test_backdoor_bad(self):
        with self.app.test_request_context('/json/tower',
                headers={'Authorization': 'Backdoor backdoor'}):
            self.assertFalse(check_backdoor())

    def test_backdoor_good(self):
        with self.app.test_request_context('/json/overview'):
            self.assertFalse(check_backdoor())

        with self.app.test_request_context('/json/overview',
                headers={'Authorization': 'Backdoor backdoor'}):
            self.assertTrue(check_backdoor())

def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(BackdoorTestCase))
    return suite

