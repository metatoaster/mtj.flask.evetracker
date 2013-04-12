from __future__ import absolute_import

from flask import Blueprint, Flask, request, g, make_response, render_template

from mtj.eve.tracker.frontend.flask import json_frontend

from mtj.flask.evetracker import util
from mtj.flask.evetracker import pos

app = Flask('mtj.flask.evetracker')

@app.before_request
def before_request():
    g.navbar = app.config['MTJ_FLASK_NAV']

    json_prefix = app.config.get('MTJPOSTRACKER_JSON_PREFIX', 'json')

    # This is used by the javascript client.  Typically it is the same
    # instance as this.
    json_script_root = request.script_root
    # Alternatively a different one may be specified, but must be
    # accessible by the target end users.  This is for advanced usage.
    # json_script_root = 'http://example.com/mtj.eve.tracker/frontend'

    g.json_root = json_script_root + json_prefix

@app.teardown_request
def teardown_request(exception):
    pass

util.register_blueprint_navbar(app, pos.overview, url_prefix='/overview')
util.register_blueprint_navbar(app, pos.tower, url_prefix='/tower')

app.wsgi_app = util.ReverseProxied(app.wsgi_app)
