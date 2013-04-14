import os
import tempfile

from unittest import TestCase, TestSuite, makeSuite
from mtj.flask.evetracker import app


class EveTrackerTestCase(TestCase):

    def setUp(self):
        self.fd, app.config['DATABASE'] = tempfile.mkstemp()
        self.app = app.test_client()

    def tearDown(self):
        os.close(self.fd)
        os.unlink(app.config['DATABASE'])

    def test_home(self):
        rv = self.app.get('/')
        self.assertTrue('POS Tracker' in rv.data)


def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(EveTrackerTestCase))
    return suite

