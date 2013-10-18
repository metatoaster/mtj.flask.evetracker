import random
import hmac
from hashlib import sha1 as sha

from mtj.flask.acl import flask

csrf_key = '_authenticator'


def randstr(b=128, r=None):
    if r is None:
        try:
            r = random.SystemRandom().getrandbits
        except:
            r = random.getrandbits

    return (('%%%ds' % (b / 4)) % hex(r(b))[2:]).replace(' ', '0')


class Authenticator(object):
    """
    CSRF protection authenticator
    """

    def __init__(self, secret=None):
        if secret is None:
            secret = randstr()

        self.secret = secret

    def getSecretFor(self, username=None):
        """
        Generate user specific user secret.
        """

        if username is None:
            username = flask.getCurrentUser().login

        return hmac.new(self.secret, username, sha).hexdigest()

    def render(self, username=None):
        return '<input type="hidden" name="%s" value="%s" />' % (
            csrf_key, self.getSecretFor(username))
