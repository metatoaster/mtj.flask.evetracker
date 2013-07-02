from unittest import TestCase, TestSuite, makeSuite
from mtj.flask.evetracker.acl import sql


class AclTestCase(TestCase):

    def setUp(self):
        self.auth = sql.SqlAcl()

    def tearDown(self):
        pass

    def test_core_acl(self):
        auth = self.auth
        auth.register('admin', 'password')
        users = auth.listUsers()
        self.assertEqual(users[0].login, 'admin')
        self.assertNotEqual(users[0].password, 'password')

        self.assertFalse(auth.authenticate('admin', 'nope'))
        self.assertTrue(auth.authenticate('admin', 'password'))

    def test_list_users(self):
        auth = self.auth
        auth.register('admin', 'password')
        auth.register('user', 'secret')
        users = auth.listUsers()
        self.assertEqual(users[0].login, 'admin')
        self.assertNotEqual(users[0].password, 'password')
        self.assertEqual(users[1].login, 'user')
        self.assertNotEqual(users[1].password, 'secret')

        self.assertEqual(auth.getUser('admin').login, 'admin')
        self.assertEqual(auth.getUser('user').login, 'user')

    def test_dupe_register(self):
        auth = self.auth
        self.assertTrue(auth.register('admin', 'password'))
        self.assertFalse(auth.register('admin', 'password', 'bad@example.com'))

    def test_bad_login(self):
        auth = self.auth
        self.assertFalse(auth.authenticate('admin', 'password'))
        self.assertFalse(auth.authenticate('no', 'user'))

    def test_group_base(self):
        auth = self.auth
        auth.addGroup('admin')
        auth.addGroup('user', 'Normal users')

        groups = auth.listGroups()
        self.assertEqual(groups[0].name, 'admin')
        self.assertEqual(groups[1].name, 'user')
        self.assertEqual(groups[1].description, 'Normal users')

    def test_user_group(self):
        auth = self.auth
        auth.register('admin', 'password')
        auth.addGroup('admin')
        auth.addGroup('user')

        self.assertEqual(auth.getUserGroups('admin'), ())
        auth.setUserGroups('admin', ('admin',))
        self.assertEqual(auth.getUserGroups('admin'), ('admin',))
        auth.setUserGroups('admin', ('user',))
        self.assertEqual(auth.getUserGroups('admin'), ('user',))
        auth.setUserGroups('admin', ('user', 'admin'))
        self.assertEqual(auth.getUserGroups('admin'), ('admin', 'user',))

        # Addition of non-existent groups fail silently.
        auth.setUserGroups('admin', ('user', 'nimda'))
        self.assertEqual(auth.getUserGroups('admin'), ('user',))


def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(AclTestCase))
    return suite

