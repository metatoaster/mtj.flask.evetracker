import logging

from passlib.hash import sha256_crypt

import sqlalchemy
from sqlalchemy import Column, Integer, String, MetaData
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from mtj.flask.evetracker.acl import BaseAcl

Base = declarative_base()

logger = logging.getLogger('mtj.flask.evetracker.sqlacl')


class User(Base):

    __tablename__ = 'user'

    login = Column(String(255), primary_key=True)
    password = Column(String(255))
    name = Column(String(255))
    email = Column(String(255))

    def __init__(self, login, password, name=None, email=None, *a, **kw):
        self.login = login
        self.password = sha256_crypt.encrypt(password)
        self.name = name
        self.email = email


class Group(Base):

    __tablename__ = 'group'

    name = Column(String(255), primary_key=True)
    description = Column(String(255))

    def __init__(self, name, description):
        self.name = name
        self.description = description


class UserGroup(Base):

    __tablename__ = 'user_group'

    id = Column(Integer, primary_key=True)
    user = Column(String(255), index=True)
    group = Column(String(255), index=True)

    def __init__(self, user, group):
        self.user = user
        self.group = group


class SqlAcl(BaseAcl):
    """
    Low level SQLAlchemy basd ACL backend.
    """

    def __init__(self, src=None, *a, **kw):
        # XXX for the session/access token table.
        super(SqlAcl, self).__init__(*a, **kw)

        if not src:
            src = 'sqlite://'

        self._conn = create_engine(src)
        self._metadata = MetaData()
        self._metadata.reflect(bind=self._conn)
        Base.metadata.create_all(self._conn)
        self._sessions = sessionmaker(
            bind=self._conn,
        )

        self.src = src

    def session(self):
        return self._sessions()

    def validate(self, login, password):
        user = self.getUser(login)
        if user is None:
            # Data leakage potential via timing attack.  Mitigation: 
            # generate a new crypt to emuluate the time spent on
            # crypting/comparing the result.
            # TODO verify timings as crypt.verify does a bit more than
            # this.
            sha256_crypt.encrypt(password)
            return False

        result = sha256_crypt.verify(password, user.password)
        return result

    def register(self, *a, **kw):
        u = User(*a, **kw)
        if self.getUser(u.login):
            return False

        session = self.session()
        session.add(u)
        session.commit()
        return True

    def listUsers(self):
        session = self.session()
        q = session.query(User)
        return q.all()

    def getUser(self, login):
        session = self.session()
        q = session.query(User).filter(User.login == login)
        session.close()
        return q.first()

    def addGroup(self, name, description=None):
        g = Group(name, description)
        session = self.session()
        session.add(g)
        session.commit()

    def listGroups(self):
        session = self.session()
        q = session.query(Group)
        return q.all()

    def setUserGroups(self, user, groups):
        all_groups = {g.name for g in self.listGroups()}
        session = self.session()
        session.query(UserGroup).filter(UserGroup.user == user).delete()
        for group in groups:
            if group not in all_groups:
                continue
            session.add(UserGroup(user, group))
        session.commit()

    def getUserGroups(self, user):
        session = self.session()
        q = session.query(UserGroup).filter(UserGroup.user == user)
        results = []
        for ug in q.all():
            results.append(ug.group)
        results = tuple(sorted(results))
        session.close()
        return results
