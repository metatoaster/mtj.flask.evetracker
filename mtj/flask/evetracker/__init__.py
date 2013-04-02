from __future__ import absolute_import

from flask import Blueprint, Flask, request, g, make_response, render_template

from mtj.flask.evetracker.pos import overview, details

app = Flask('mtj.flask.evetracker')

@app.before_request
def before_request():
    g.navbar = app.blueprints.keys()

@app.teardown_request
def teardown_request(exception):
    pass

app.register_blueprint(overview, url_prefix='/overview')
app.register_blueprint(details, url_prefix='/details')