Introduction
============

This is a relatively barebone reference front end for mtj.eve.tracker.
Currently provides a basic set of HTML5 templates rendered using flask
that loads data from the JSON end-point embedded within the root app
object.

Currently there are *no* tests written for this but this will be done
once the designs are completely finalized (and once I find time to do
this as getting the backend working took all my time).  However, if you
really want to see how this works, please use `mtj.eve.buildout`_ to
grab this along with all the dependencies.

.. _mtj.eve.buildout: https://github.com/metatoaster/mtj.eve.buildout

Once the buildout finishes, do this::

    $ bin/python src/mtj.flask.evetracker/mtj/flask/evetracker/ctrl.py
    mtj.tracker.ctrl> write_config config.json
    mtj.tracker.ctrl> ^C

This will write out a barebone config.  You will need to fill out these
crucial information in JSON format:

logging / path

    Where your logs go

mtj.eve.tracker.runner.FlaskRunner / json_prefix

    Where the json blueprint will be placed.  Try '/json'.

mtj.eve.tracker.runner.FlaskRunner / admin_key

    Set it to something so the externally running import command can
    notify the running instance to reload the data from database.

data / backend_url

    Set it to some SQLAlchemy compatible path to your database source.
    If unsure just use ``sqlite:////tmp/test.db``.

data / evedb_url

    This one you need to get for yourself.  Either use the community
    provided db dumps which will provide all the complete data, or you
    may `download`_ a reduced datadump for this.

    Once you set up the download link, decompress it and then reference
    this file using the same SQLAlchemy path.

.. _download: http://img.metatoaster.com/eve/ret107.mtj.pos.tracker.sqlite.bz2

data / evelink_cache

    Where the evelink caches go.  Give this some path so CCP doesn't ban
    you or your host from using ther API.

api / api_keys

    The API keys are in a key:value pair format, and they must be your
    corp key.  The format within that config file looks like this:
    ``"123456": "keyspecificvcodeforyourstuff"``

user / mode

    Change this to ``"setup"`` so you can log in using the setup_login
    and setup_password combination.

Now you got that out of the way, you can try to start the instance like
so::

    $ bin/python src/mtj.flask.evetracker/mtj/flask/evetracker/ctrl.py \
    >     -c config.json fg
    2013-04-01 00:00:00 INFO mtj.eve.tracker.runner EveTrackerRunner starting up
    2013-04-01 00:00:00 INFO mtj.eve.tracker.runner Instantiating towers from database.
    2013-04-01 00:00:00 INFO mtj.eve.tracker.backend.sql Reinstantiation requested.
    2013-04-01 00:00:00 INFO mtj.eve.tracker.backend.sql 0 towers to reinstantiate.
    2013-04-01 00:00:00 INFO mtj.eve.tracker.backend.sql (0/0) towers reinstantiated.
    2013-04-01 00:00:00 INFO mtj.eve.tracker.runner No json_prefix defined; tracker will not serve JSON.
    2013-04-01 00:00:00 INFO werkzeug  * Running on http://127.0.0.1:8000/

Now in another terminal window, you can try to update the tracker using
live data from the EVE API::

    $ bin/python src/mtj.flask.evetracker/mtj/flask/evetracker/ctrl.py \
    >     -c config.json import -u
    Notice: `http://127.0.0.1:8000/json/reload` will be notified of update.

Now wait for the API to pull the data.  If everything was set up 
correctly this will happen in that console::

    {"status": "ok", "result": "212 towers reloaded."}

In your other console, you should see something like this::

    2013-04-01 00:03:00 INFO mtj.eve.tracker.backend.sql Reinstantiation requested.
    2013-04-01 00:03:00 INFO mtj.eve.tracker.backend.sql 212 towers to reinstantiate.
    2013-04-01 00:03:03 INFO mtj.eve.tracker.backend.sql (212/212) towers reinstantiated.

Now you should be able to point your browser to http://127.0.0.1:8000,
and login using the credentials specified in the user section, and see
how your (or your espionage targets') towers are faring.
