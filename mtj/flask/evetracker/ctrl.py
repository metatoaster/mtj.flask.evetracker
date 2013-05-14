from __future__ import unicode_literals  # we are using json anyway.

import importlib

from mtj.eve.tracker.ctrl import FlaskRunner, Options, main
from mtj.flask.evetracker import app
from mtj.flask.evetracker import acl
from mtj.flask.evetracker import csrf
from mtj.flask.evetracker import user


class EveTrackerOptions(Options):

    # Doing it the long way to not pollute the parent class.
    default_config = {}
    default_config.update(Options.default_config)
    default_config.update({
        'users': {
            'mode': 'default',
            'setup_login': 'admin',
            'setup_password': 'password',
            'class': None,
            'kwargs': None,
        },
        'acl': {
            'logged_in': 'logged_in',
        },
    })

    _schema = {}
    _schema.update(Options._schema)
    _schema.update({
        'users': {
            'mode': ('default', 'setup', 'class_path',),
            'setup_login': basestring,
            'setup_password': basestring,
            'class_path': basestring,
            'kwargs': dict,
        },
        'acl': {
            'logged_in': basestring,
        },
    })


class EveTrackerRunner(FlaskRunner):

    def configure(self, config):
        super(FlaskRunner, self).configure(config)

        users = config.get('users')
        mode = users.get('mode')

        if mode == 'setup':
            self.acl = acl.SetupAcl(users.get('setup_login'),
                users.get('setup_password'))
        elif mode == 'default':
            # Not really implemented
            self.acl = acl.BaseAcl()
        elif mode == 'class_path':
            mod, clsname = users.get('class_path').rsplit('.', 1)
            kwargs = users.get('kwargs') or {}
            cls = getattr(importlib.import_module(mod), clsname)
            self.acl = cls(**kwargs)

    def prepare(self, app):
        super(EveTrackerRunner, self).prepare(app)
        app.config['MTJ_ACL'] = self.acl
        # persist the secret so a form rendered before restart works
        # afterwards, but this maybe a security feature...
        app.config['MTJ_CSRF'] = csrf.Authenticator()
        # allow overriding and not depending on import user
        app.config['MTJ_CURRENT_USER'] = user.getCurrentUser
        app.config['MTJ_LOGGED_IN'] = self.config.get('acl').get('logged_in')


if __name__ == "__main__":
    main(options=EveTrackerOptions(), app=app, runner_factory=EveTrackerRunner)
