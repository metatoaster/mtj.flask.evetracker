class BaseAcl(object):

    def __init__(self, *a, **kw):
        pass

    def validate(self, login, password):
        return False


class SetupAcl(object):
    def __init__(self, login, password):
        self.login = login
        self.password = password

    def validate(self, login, password):
        return self.login == login and self.password == password


class SqlAlchemy(object):

    def __init__(self, src):
        self.src = src

    def validate(self, login, password):
        raise NotImplementedError
