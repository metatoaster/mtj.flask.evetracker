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

    def test_edit_user(self):
        auth = self.auth
        auth.register('user', 'password')
        user = auth.getUser('user')
        self.assertEqual(user.name, None)
        self.assertEqual(user.email, None)
        auth.editUser('user', 'User Name', 'user@example.com')
        user = auth.getUser('user')
        self.assertEqual(user.name, 'User Name')
        self.assertEqual(user.email, 'user@example.com')

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
        auth.addGroup('user', 'Normal users')

        groups = auth.listGroups()
        # builtin.
        self.assertEqual(groups[0].name, 'admin')
        self.assertEqual(groups[1].name, 'user')
        self.assertEqual(groups[1].description, 'Normal users')

        self.assertEqual(auth.getGroup('user').description, 'Normal users')

    def test_user_group(self):
        def filter_gn(groups):
            results = [ug.name for ug in groups]
            return tuple(sorted(results))

        auth = self.auth
        auth.register('admin', 'password')
        auth.addGroup('user')

        admin_user = auth.getUser('admin')

        self.assertEqual(filter_gn(auth.getUserGroups(admin_user)), ())
        auth.setUserGroups(admin_user, ('admin',))
        self.assertEqual(filter_gn(auth.getUserGroups(admin_user)), ('admin',))
        auth.setUserGroups(admin_user, ('user',))
        self.assertEqual(filter_gn(auth.getUserGroups(admin_user)), ('user',))
        auth.setUserGroups(admin_user, ('user', 'admin'))
        self.assertEqual(filter_gn(auth.getUserGroups(admin_user)),
            ('admin', 'user',))

        # Addition of non-existent groups fail silently.
        auth.setUserGroups(admin_user, ('user', 'nimda'))
        self.assertEqual(filter_gn(auth.getUserGroups(admin_user)), ('user',))

    def test_setup_login(self):
        auth = sql.SqlAcl(setup_login='admin')
        self.assertEqual(auth.getUser('admin'), None)
        auth = sql.SqlAcl(setup_login='admin', setup_password='password')
        self.assertEqual(auth.getUser('admin').login, 'admin')
        self.assertTrue(auth.authenticate('admin', 'password'))

        admin_grp = auth.getGroup('admin')
        self.assertEqual(admin_grp.name,
            auth.getUserGroups(auth.getUser('admin'))[0].name)

        # revoke admin
        auth.setUserGroups(auth.getUser('admin'), ())
        auth._registerAdmin('admin', 'password')
        # Should not have any groups as this login was previously
        # registered.
        self.assertEqual(len(auth.getUserGroups(auth.getUser('admin'))), 0)


def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(AclTestCase))
    return suite

