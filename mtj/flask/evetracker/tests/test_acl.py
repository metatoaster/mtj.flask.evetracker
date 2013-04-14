from unittest import TestCase, TestSuite, makeSuite
from mtj.flask.evetracker import acl


class AclTestCase(TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_setup_acl(self):
        auth = acl.SetupAcl('admin', 'password')
        self.assertEqual(auth.authenticate('test', 'password'), False)
        self.assertEqual(auth.authenticate('admin', 'password'), {
            'user': 'admin',
            'groups': ['admin'],
        })


def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(AclTestCase))
    return suite

