import time


class BaseUser(object):

    def __init__(self, login, *a, **kw):
        self.login = login

    def __str__(self):
        return self.login

    def __repr__(self):
        return '<BaseUser>'


class AnonymousUser(BaseUser):

    def __init__(self, login=None, *a, **kw):
        self.login = '<Anonymous>'
        self.anonymous = True

    def __str__(self):
        return 'SpecialUser:Anonymous'

    def __repr__(self):
        return '<AnonymousUser>'

anonymous = AnonymousUser()


class BaseGroup(object):

    def __init__(self, name, description, *a, **kw):
        self.name = name
        self.description = description


class BaseAcl(object):

    def __init__(self, *a, **kw):
        self._tbl_access_tokens = {}

    def authenticate(self, login, password):
        if self.validate(login, password):
            return self.generateAccessToken(login)
        return False

    def validate(self, login, password):
        return False

    def getUser(self, user):
        return anonymous

    def generateAccessToken(self, login):
        """
        Store and return an access token.
        """

        ts = time.time()
        if login not in self._tbl_access_tokens:
            self._tbl_access_tokens[login] = []

        self._tbl_access_tokens[login].append(ts)

        access_token = {
            'login': login,
            'ts': ts,
        }

        return access_token

    def validateAccessToken(self, access_token):
        login = access_token.get('login')
        ts = access_token.get('ts')

        return ts in self._tbl_access_tokens.get(login, [])

    def getUserFromAccessToken(self, access_token):
        if not self.validateAccessToken(access_token):
            return anonymous

        return self.getUser(access_token['login'])

    def getUserGroups(self, login):
        return []

    def listUsers(self):
        return []

    def updatePassword(self, login, password):
        return False


class SetupAcl(BaseAcl):

    admin_user = BaseUser('admin')
    admin_group = BaseGroup('admin', 'Setup Admin Group')

    def __init__(self, login, password, *a, **kw):
        super(SetupAcl, self).__init__(*a, **kw)
        self.login = login
        self.password = password

    def validate(self, login, password):
        return login in (self.login, 'admin') and self.password == password

    def getUser(self, user):
        if user == self.admin_user.login:
            return self.admin_user

        if user == self.login:
            return BaseUser(self.login)

        return anonymous

    def getUserGroups(self, user):
        if user == self.admin_user:
            return [self.admin_group]
        return []

    def listUsers(self):
        return [self.admin_user, BaseUser(self.login)]
