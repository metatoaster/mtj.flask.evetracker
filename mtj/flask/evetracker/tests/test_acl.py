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
        result = auth.authenticate('admin', 'password')
        self.assertEqual(result['login'], 'admin')

    def test_access_token(self):
        auth = acl.SetupAcl('admin', 'password')
        token = auth.generateAccessToken('admin')
        self.assertEqual(token['login'], 'admin')
        self.assertTrue(auth.validateAccessToken(token))
        token['ts'] = 0
        self.assertFalse(auth.validateAccessToken(token))

        token = auth.generateAccessToken('user')
        self.assertEqual(sorted(auth._tbl_access_tokens.keys()),
            ['admin', 'user'])


def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(AclTestCase))
    return suite

