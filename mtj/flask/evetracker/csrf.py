import random
import hmac
from hashlib import sha1 as sha

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

    def getSecretFor(self, username):
        """
        Generate user specific user secret.
        """

        return hmac.new(self.secret, username, sha).hexdigest()
