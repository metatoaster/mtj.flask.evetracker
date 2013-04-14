from __future__ import absolute_import

from flask import Blueprint, Flask, request, g, make_response, render_template
from flask import session, redirect, url_for, abort

from mtj.eve.tracker.frontend.flask import json_frontend

from mtj.flask.evetracker import util
from mtj.flask.evetracker import pos
from mtj.flask.evetracker import user

app = Flask('mtj.flask.evetracker')

white_list = ['acl_front', None]

@app.before_request
def before_request():
    if not session.get('logged_in'):
        g.navbar = []
        g.aclbar = [('log in', '/acl/login')]
        if request.blueprint not in white_list:
            abort(401)
    else:
        set_logged_in_g()

def set_logged_in_g():
    g.navbar = app.config['MTJ_FLASK_NAV']
    g.aclbar = [
        (user.getCurrentUser(), '/acl/current'),
        ('logout', '/acl/logout'),
    ]

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

@app.route('/')
def app_index():
    result = render_template('index.jinja')
    response = make_response(result)
    return response

util.register_blueprint_navbar(app, pos.overview, url_prefix='/overview')
util.register_blueprint_navbar(app, pos.tower, url_prefix='/tower')

app.register_blueprint(user.acl_front, url_prefix='/acl')

app.wsgi_app = util.ReverseProxied(app.wsgi_app)

# Uncomment if debug:
#app.wsgi_app = util.PdbPostMortemLayer(app.wsgi_app)
