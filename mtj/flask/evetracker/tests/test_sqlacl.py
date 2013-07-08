from unittest import TestCase, TestSuite, makeSuite

from flask import Flask, session
from werkzeug.exceptions import Forbidden

import mtj.flask.evetracker

from mtj.flask.evetracker.acl import sql
from mtj.flask.evetracker import user


class AclTestCase(TestCase):

    def setUp(self):
        self.auth = sql.SqlAcl()

    def tearDown(self):
        pass

    def test_core_acl(self):
        auth = self.auth
        self.assertTrue(auth.register('admin', 'password'))
        users = auth.listUsers()
        self.assertEqual(users[0].login, 'admin')
        self.assertNotEqual(users[0].password, 'password')

        self.assertFalse(auth.authenticate('admin', 'nope'))
        self.assertTrue(auth.authenticate('admin', 'password'))

    def test_too_short_password(self):
        # too short of a password
        self.assertFalse(self.auth.register('admin', ''))
        self.assertFalse(self.auth.register('admin', '1'))

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

    def test_edit_passwd(self):
        auth = self.auth
        auth.register('user', 'password')
        user = auth.getUser('user')
        self.assertTrue(auth.validate('user', 'password'))

        self.assertFalse(auth.updatePassword('user', None))
        self.assertTrue(auth.validate('user', 'password'))

        self.assertFalse(auth.updatePassword('user', 'short'))
        self.assertTrue(auth.validate('user', 'password'))

        self.assertTrue(auth.updatePassword('user', 'secret'))
        self.assertFalse(auth.validate('user', 'password'))
        self.assertTrue(auth.validate('user', 'secret'))

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


class UserSqlAclIntegrationTestCase(TestCase):

    def setUp(self):
        app = Flask('mtj.flask.evetracker')
        app.config['MTJ_ACL'] = self.auth = sql.SqlAcl(
            setup_login='admin', setup_password='password')
        app.config['SECRET_KEY'] = 'test_secret_key'
        app.config['MTJ_LOGGED_IN'] = 'test_logged_in_token'
        app.register_blueprint(user.acl_front, url_prefix='/acl')

        app.config['TESTING'] = True
        self.app = app
        self.client = self.app.test_client()

        with self.client as c:
            rv = c.post('/acl/login',
                data={'login': 'admin', 'password': 'password'})

    def test_list_user(self):
        with self.client as c:
            rv = c.get('/acl/list')
            self.assertTrue('<td>admin</td>' in rv.data)

    def test_add_user(self):
        with self.client as c:
            rv = c.get('/acl/add')
            self.assertTrue('name="name" value=""' in rv.data)
            self.assertTrue('name="email" value=""' in rv.data)

            rv = c.post('/acl/add', data={
                'login': 'user',
                'password': 'userpassword',
                'name': 'User Name',
                'email': 'user@example.com',
            })
            self.assertEqual(rv.headers['location'],
                'http://localhost/acl/edit/user')

            r2 = c.get('/acl/edit/user')

            self.assertTrue('name="login" value="user"' in r2.data)
            self.assertTrue('name="name" value="User Name"' in r2.data)
            self.assertTrue('name="email" value="user@example.com"' in r2.data)

        with self.app.test_client() as c:
            # Now try logging in using the newly added user.
            rv = c.post('/acl/login',
                data={'login': 'user', 'password': 'userpassword'})
            self.assertEqual(rv.headers['location'],
                'http://localhost/')

            rv = c.get('/acl/current')
            self.assertTrue('Welcome user' in rv.data)

    def test_edit_user(self):
        with self.client as c:
            rv = c.get('/acl/edit/admin')
            self.assertTrue('name="name" value=""' in rv.data)
            self.assertTrue('name="email" value=""' in rv.data)

            rv = c.post('/acl/edit/admin',
                data={'name': 'User Name', 'email': 'user@example.com'})
            self.assertTrue('name="name" value="User Name"' in rv.data)
            self.assertTrue('name="email" value="user@example.com"' in rv.data)

    def test_passwd(self):
        with self.app.test_client() as c:
            rv = c.post('/acl/login',
                data={'login': 'admin', 'password': 'password'})

            # kind of a waste repeating it here but eh.
            rv = c.post('/acl/passwd')
            self.assertTrue('Please fill out all the required fields.'
                in rv.data)

            rv = c.post('/acl/passwd', data={
                'old_password': 'fail', 'password': 'newpassword',
                'confirm_password': 'failure'})
            self.assertTrue('Old password incorrect' in rv.data)

            rv = c.post('/acl/passwd', data={
                'old_password': 'password', 'password': 'newpassword',
                'confirm_password': 'failure'})
            self.assertTrue('Password and confirmation password mismatched.'
                in rv.data)

            rv = c.post('/acl/passwd', data={
                'old_password': 'password', 'password': '1',
                'confirm_password': '1'})
            self.assertTrue('New password too short.' in rv.data)

            rv = c.post('/acl/passwd', data={
                'old_password': 'password', 'password': '123456',
                'confirm_password': '123456'})
            self.assertTrue(self.auth.validate('admin', '123456'))


def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(AclTestCase))
    suite.addTest(makeSuite(UserSqlAclIntegrationTestCase))
    return suite

