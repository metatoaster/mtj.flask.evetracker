from __future__ import absolute_import

from flask import Blueprint, Flask, request, g, make_response, render_template
from flask import session, redirect, url_for, abort, current_app

from werkzeug.exceptions import HTTPException

from mtj.eve.tracker.frontend.flask import json_frontend

from mtj.flask.evetracker import csrf
from mtj.flask.evetracker import util
from mtj.flask.evetracker import pos
from mtj.flask.evetracker import user

app = Flask('mtj.flask.evetracker')

public_blueprints = {
    None: None,
    'acl_front': None,
    'json_frontend': ['json_frontend.reload_db'],
}

@app.before_request
def before_request():
    if not session.get('logged_in'):
        # set the nav elements first.
        g.navbar = []
        g.aclbar = [('log in', '/acl/login')]

        if request.blueprint in public_blueprints:
            paths = public_blueprints[request.blueprint]
            if paths is None or request.url_rule.endpoint in paths:
                # Unspecified paths are all whitelists, or it's validated
                # against the list of permissible endpoints.
                return

        abort(401)
    else:
        set_logged_in_g()

@app.before_request
def csrf_protect():
    current_user = user.getCurrentUser()
    if current_user == user.anonymous:
        # zero protection for anonymous users.
        return

    if request.method == 'POST':
        token = request.form.get(csrf.csrf_key)
        if token != current_app.config['MTJ_CSRF'].getSecretFor(current_user):
            abort(403)

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

@app.errorhandler(401)
def http_401(error):
    return render_template('http.401.jinja'), error.code

@app.errorhandler(402)
@app.errorhandler(403)
@app.errorhandler(404)
@app.errorhandler(405)
@app.errorhandler(406)
@app.errorhandler(407)
@app.errorhandler(410)
def http_401(error):
    if isinstance(error, HTTPException):
        return render_template('http.error.jinja', error=error,
            http_error_msg=error.description), error.code
    else:
        raise error

util.register_blueprint_navbar(app, pos.overview, url_prefix='/overview')
util.register_blueprint_navbar(app, pos.tower, url_prefix='/tower')

app.register_blueprint(user.acl_front, url_prefix='/acl')

app.wsgi_app = util.ReverseProxied(app.wsgi_app)

# Uncomment if debug:
#app.wsgi_app = util.PdbPostMortemLayer(app.wsgi_app)
#@app.errorhandler(500)
#def http_500(error):
#    import pdb;pdb.set_trace()
#    raise error
