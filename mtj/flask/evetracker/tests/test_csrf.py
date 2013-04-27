from unittest import TestCase, TestSuite, makeSuite
from mtj.flask.evetracker import csrf


class CsrfTestCase(TestCase):

    def setUp(self):
        self.csrf = csrf.Authenticator(secret='foobartestsecret')

    def tearDown(self):
        pass

    def test_csrf(self):
        self.assertEqual(self.csrf.getSecretFor('username'),
            '857c28b1c5f87bfe312fc7df185a782a6bb46cad')


def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(CsrfTestCase))
    return suite

