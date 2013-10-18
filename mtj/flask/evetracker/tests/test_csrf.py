from unittest import TestCase, TestSuite, makeSuite
from flask import Flask, session, g
from werkzeug.exceptions import Forbidden

from mtj.flask.acl.base import BaseUser, anonymous

from mtj.flask.evetracker import csrf

from mtj.flask.evetracker.hooks import csrf_protect


class DummyACL(object):
    def getUserFromAccessToken(self, access_token):
        return session.get('dummy_user', anonymous)


class RandTestCase(TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_core(self):
        self.assertEqual('0' * 32, csrf.randstr(b=128, r=lambda x: 0))
        self.assertEqual('0' * 31, csrf.randstr(b=124, r=lambda x: 0))
        self.assertEqual('0' * 30 + '1', csrf.randstr(b=124, r=lambda x: 1))


class CsrfTestCase(TestCase):

    def setUp(self):
        self.csrf = csrf.Authenticator(secret='foobartestsecret')

    def tearDown(self):
        pass

    def test_csrf(self):
        self.assertEqual(self.csrf.getSecretFor('username'),
            '857c28b1c5f87bfe312fc7df185a782a6bb46cad')

    def test_render(self):
        self.assertTrue(self.csrf.render('username').startswith(
            '<input type="hidden"'))


class CsrfFlaskTestCase(TestCase):
    """
    Test the intergration of the protection into the core app.
    """

    def setUp(self):
        self.app = Flask('mtj.flask.evetracker')

        self.app.config['PRESERVE_CONTEXT_ON_EXCEPTION'] = True
        self.app.config['SECRET_KEY'] = 'test_secret_key'
        self.app.config['MTJ_CSRF'] = csrf.Authenticator(
            secret='foobartestsecret')
        self.app.config['MTJ_ACL'] = DummyACL()

    def tearDown(self):
        pass

    def test_csrf_protect_no_user(self):
        # not intercepted, not logged in.
        with self.app.test_request_context('/', method='POST'):
            self.assertTrue(csrf_protect() is None)

    def test_csrf_protect_user_no_token(self):
        # intercepted, logged in.
        with self.app.test_request_context('/', method='POST'):
            g.mtj_user = BaseUser('username')
            self.assertRaises(Forbidden, csrf_protect)

    def test_csrf_protect_user_with_token(self):
        # intercepted, logged in.
        with self.app.test_request_context('/', method='POST',
                data={'_authenticator':
                    '857c28b1c5f87bfe312fc7df185a782a6bb46cad'}):
            g.mtj_user = BaseUser('username')
            # could use a better way to test this.
            # a before_request method cannot return a value as it will
            # interfere with the wsgi stack.
            self.assertTrue(csrf_protect() is None)


def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(RandTestCase))
    suite.addTest(makeSuite(CsrfTestCase))
    suite.addTest(makeSuite(CsrfFlaskTestCase))
    return suite

