import random
import hmac
from hashlib import sha1 as sha

from mtj.flask.evetracker import user

csrf_key = '_authenticator'


def randstr(b=128):
    try:
        r = random.SystemRandom()
    except:
        r = random

    return ('%x' % r.getrandbits(b)).decode('hex')


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
            username = user.getCurrentUser().login

        return hmac.new(self.secret, username, sha).hexdigest()

    def render(self, username=None):
        return '<input type="hidden" name="%s" value="%s" />' % (
            csrf_key, self.getSecretFor(username))
