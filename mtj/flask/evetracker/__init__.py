from __future__ import absolute_import

from urllib import quote_plus

from flask import Blueprint, Flask, request, g, make_response, render_template
from flask import session, redirect, url_for, abort, current_app

from werkzeug.exceptions import HTTPException

from mtj.eve.tracker.frontend.flask import json_frontend

from mtj.flask.acl.sql import SqlAcl
from mtj.flask.acl.user import make_acl_front
from mtj.flask.acl.base import anonymous
from mtj.flask.acl.flask import getCurrentUser, getCurrentUserRoles

from mtj.flask.evetracker import util
from mtj.flask.evetracker import pos
from mtj.flask.evetracker import audit

acl_front = make_acl_front(layout='layout.jinja')

app = Flask('mtj.flask.evetracker')
# welp, I made the mistake of naming all filenames with .jinja..
# so no autoescape.  Forcing it all to be true.
app.jinja_env.autoescape = True

@app.teardown_request
def teardown_request(exception):
    pass

@app.route('/')
def app_index():
    # TODO make this configurable?
    return redir_app_index()

def redir_app_index():
    return redirect(url_for('overview.overview_index'))

def static_app_index():
    result = render_template('index.jinja')
    response = make_response(result)
    return response

@app.errorhandler(401)
def http_401(error):
    target = quote_plus(request.path)
    return render_template('http.401.jinja', target=target), error.code

@app.errorhandler(402)
@app.errorhandler(403)
@app.errorhandler(404)
@app.errorhandler(405)
@app.errorhandler(406)
@app.errorhandler(407)
@app.errorhandler(410)
def http_error(error):
    if isinstance(error, HTTPException):
        return render_template('http.error.jinja', error=error,
            http_error_msg=error.description), error.code
    else:
        raise error

util.register_blueprint_navbar(app, pos.overview, url_prefix='/overview',
    permit='pos_viewer')
util.register_blueprint_navbar(app, pos.tower, url_prefix='/tower',
    permit='pos_viewer')
util.register_blueprint_navbar(app, audit.audit, url_prefix='/audit',
    permit='audit_viewer')

app.register_blueprint(acl_front, url_prefix='/acl')

app.wsgi_app = util.ReverseProxied(app.wsgi_app)

# Uncomment if debug:
#app.wsgi_app = util.PdbPostMortemLayer(app.wsgi_app)
#@app.errorhandler(500)
#def http_500(error):
#    import pdb;pdb.post_mortem()
#    raise error
