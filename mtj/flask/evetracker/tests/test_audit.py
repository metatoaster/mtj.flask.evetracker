import os
import unittest

from flask import Flask, session, g

import zope.component

from flask.ext.principal import identity_changed, identity_loaded
from flask.ext.principal import Identity, RoleNeed, Principal

from mtj.flask.acl.base import BaseUser, BaseAcl
from mtj.flask.acl import csrf

from mtj.eve.tracker.interfaces import ITrackerBackend
import mtj.flask.evetracker

from mtj.flask.evetracker import audit

from mtj.eve.tracker.tests import base

testuser = BaseUser('test_user')


class AuditTestCase(unittest.TestCase):

    def setUp(self):
        base.setUp(self)
        app = Flask('mtj.flask.evetracker')
        Principal(app)

        app.config['SECRET_KEY'] = 'test_secret_key'
        app.config['MTJ_CURRENT_USER'] = lambda: testuser
        app.register_blueprint(audit.audit, url_prefix='/audit')

        app.config['TESTING'] = True
        app.config['PRESERVE_CONTEXT_ON_EXCEPTION'] = True
        app.config['MTJ_IGNORE_PERMIT'] = True
        self.app = app
        self.backend = zope.component.getUtility(ITrackerBackend)

        @app.before_request
        def force_roles():
            roles = ['raw_auditor', 'audit_viewer', 'audit_writer']
            g.identity = Identity('dummy')
            for role in roles:
                g.identity.provides.add(RoleNeed(role))

    def tearDown(self):
        base.tearDown(self)

    def test_add_audit(self):
        tower = self.backend.addTower(1000001, 12235, 30004608, 40291202, 4,
            1325376000, 1306886400, 498125261)

        with self.app.test_request_context():
            with self.app.test_client() as client:
                rv = client.post('/audit/add', data={
                    'rowid': '1',
                    'table': 'tower',
                    'reason': 'test reason',
                    'category_name': 'note',
                })

        result = list(self.backend._conn.execute('select * from audit'))
        self.assertEqual(result[0][:6], (1, u'tower', 1,
            u"test reason", u'test_user', u'note'))

    def test_add_audit_table_rowid(self):
        tower = self.backend.addTower(1000001, 12235, 30004608, 40291202, 4,
            1325376000, 1306886400, 498125261)

        with self.app.test_client() as client:
            rv = client.post('/audit/add/tower/1', data={
                'reason': 'test reason',
                'category_name': 'note',
            })

        result = list(self.backend._conn.execute('select * from audit'))
        self.assertEqual(result[0][:6], (1, u'tower', 1,
            u"test reason", u'test_user', u'note'))


if __name__ == '__main__':
    unittest.main()
