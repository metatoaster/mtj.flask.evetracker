from __future__ import unicode_literals  # we are using json anyway.

from mtj.eve.tracker.ctrl import Options, main
from mtj.flask.evetracker import app


class EvetrackerOptions(Options):

    # Doing it the long way to not pollute the parent class.
    default_config = {}
    default_config.update(Options.default_config)
    default_config.update({'users': {
        'mode': 'default',
        'setup_login': 'admin',
        'setup_password': 'password',
    }})

    _schema = {}
    _schema.update(Options._schema)
    _schema.update({'users': {
        'mode': ('default', 'setup', 'custom',),
        'setup_login': basestring,
        'setup_password': basestring,
    }})


if __name__ == "__main__":
    main(options=EvetrackerOptions(), app=app)
