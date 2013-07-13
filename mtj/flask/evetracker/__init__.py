from __future__ import absolute_import

from flask import Blueprint, Flask, request, g, make_response, render_template
from flask import session, redirect, url_for, abort, current_app

from werkzeug.exceptions import HTTPException

from mtj.eve.tracker.frontend.flask import json_frontend

from mtj.flask.evetracker.acl.flask import *

from mtj.flask.evetracker import csrf
from mtj.flask.evetracker import util
from mtj.flask.evetracker import pos
from mtj.flask.evetracker import user
from mtj.flask.evetracker import audit

app = Flask('mtj.flask.evetracker')
# welp, I made the mistake of naming all filenames with .jinja..
# so no autoescape.  Forcing it all to be true.
app.jinja_env.autoescape = True

public_blueprints = {
    None: None,
    'acl_front': None,
    'json_frontend': ['json_frontend.reload_db'],
}

backdoored_blueprints = {
    'json_frontend': ['json_frontend.overview'],
}

def check_backdoor():
    if current_app.config.get('MTJ_BACKDOOR'):
        try:
            m, auth = request.headers.get('Authorization', '').split(' ', 1)
        except ValueError:
            m, auth = '', ''

        paths = backdoored_blueprints.get(request.blueprint, None)
        return (m.lower() == 'backdoor' and 
                auth == current_app.config.get('MTJ_BACKDOOR') and
                (paths is None or request.url_rule.endpoint in paths))
    return False

@app.before_request
def before_request():
    current_user = getCurrentUser()
    if not current_user in (user.anonymous, None):
        # User is logged in.
        check_permissions()
        return

    # set the nav elements first.
    g.navbar = []
    g.aclbar = [('log in', '/acl/login')]

    if request.blueprint in public_blueprints:
        paths = public_blueprints[request.blueprint]
        if paths is None or request.url_rule.endpoint in paths:
            # Unspecified paths are all whitelists, or it's validated
            # against the list of permissible endpoints.
            return

    if check_backdoor():
        return

    abort(401)

@app.before_request
def csrf_protect():
    current_user = user.getCurrentUser()
    if current_user in (user.anonymous, None):
        # zero protection for anonymous users.
        return

    g.csrf_input = current_app.config['MTJ_CSRF'].render()

    if request.method == 'POST':
        token = request.form.get(csrf.csrf_key)
        if token != current_app.config['MTJ_CSRF'].getSecretFor(
                current_user.login):
            # TODO make this 403 specific to token failure (tell user
            # to reload the form in case of changes in hash.
            abort(403)

def check_permissions():
    # navbar
    navbar = app.config['MTJ_FLASK_NAV']

    verifyBlueprintPermit()

    set_json_root()
    g.navbar = navbar
    g.aclbar = [
        (user.getCurrentUser().login, '/acl/current'),
        ('logout', '/acl/logout'),
    ]

def set_json_root():
    json_prefix = app.config.get('MTJPOSTRACKER_JSON_PREFIX', 'json')
    # This is used by the javascript client.  Typically it is the same
    # instance as this.
    json_script_root = request.script_root
    # Alternatively a different one may be specified, but must be
    # accessible by the target end users.  This is for advanced usage.
    # XXX expose this at the config/runner level.
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
def http_error(error):
    if isinstance(error, HTTPException):
        return render_template('http.error.jinja', error=error,
            http_error_msg=error.description), error.code
    else:
        raise error

util.register_blueprint_navbar(app, pos.overview, url_prefix='/overview')
util.register_blueprint_navbar(app, pos.tower, url_prefix='/tower')
util.register_blueprint_navbar(app, audit.audit, url_prefix='/audit')

app.register_blueprint(user.acl_front, url_prefix='/acl')

app.wsgi_app = util.ReverseProxied(app.wsgi_app)

# Uncomment if debug:
#app.wsgi_app = util.PdbPostMortemLayer(app.wsgi_app)
#@app.errorhandler(500)
#def http_500(error):
#    import pdb;pdb.post_mortem()
#    raise error
