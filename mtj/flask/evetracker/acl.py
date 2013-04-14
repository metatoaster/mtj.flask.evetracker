class BaseAcl(object):

    def __init__(self, *a, **kw):
        pass

    def authenticate(self, login, password):
        if self.validate(login, password):
            return self.getAccess(login)
        return False

    def validate(self, login, password):
        return False

    def getAccess(self, login):
        return {
            'user': login,
            'groups': self.getUserGroups(login),
        }

    def getUserGroups(self, user):
        return []


class SetupAcl(BaseAcl):
    def __init__(self, login, password):
        self.login = login
        self.password = password

    def validate(self, login, password):
        return self.login == login and self.password == password

    def getUserGroups(self, user):
        return ['admin']


class SqlAcl(BaseAcl):

    def __init__(self, src):
        self.src = src

    def validate(self, login, password):
        raise NotImplementedError
