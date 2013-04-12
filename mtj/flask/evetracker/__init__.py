from __future__ import absolute_import

from flask import Blueprint, Flask, request, g, make_response, render_template

from mtj.flask.evetracker import util
from mtj.flask.evetracker import pos

app = Flask('mtj.flask.evetracker')

@app.before_request
def before_request():
    g.navbar = app.config['MTJ_FLASK_NAV']
    g.json_root = 'http://localhost:8000/json'

@app.teardown_request
def teardown_request(exception):
    pass

util.register_blueprint_navbar(app, pos.overview, url_prefix='/overview')
util.register_blueprint_navbar(app, pos.tower, url_prefix='/tower')

app.wsgi_app = util.ReverseProxied(app.wsgi_app)
