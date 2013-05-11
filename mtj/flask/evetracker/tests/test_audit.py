import os
import unittest

from flask import Flask, session

import zope.component

from mtj.eve.tracker.interfaces import ITrackerBackend
import mtj.flask.evetracker

from mtj.flask.evetracker import user
from mtj.flask.evetracker import audit
from mtj.flask.evetracker import csrf

from mtj.eve.tracker.tests import base


class AuditTestCase(unittest.TestCase):

    def setUp(self):
        base.setUp(self)
        app = Flask('mtj.flask.evetracker')
        app.config['SECRET_KEY'] = 'test_secret_key'
        app.config['MTJ_CURRENT_USER'] = lambda: 'test_user'
        app.register_blueprint(audit.audit, url_prefix='/audit')

        app.config['TESTING'] = True
        self.app = app
        self.backend = zope.component.getUtility(ITrackerBackend)

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


if __name__ == '__main__':
    unittest.main()
