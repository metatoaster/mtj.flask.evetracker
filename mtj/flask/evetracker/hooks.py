from flask import g, request, current_app, abort

from mtj.flask.acl.flask import getCurrentUser
from mtj.flask.acl.base import anonymous

from . import csrf

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

def before_request():
    g.site_root = request.script_root or '/'
    current_user = getCurrentUser()
    if not current_user in (anonymous, None):
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

def csrf_protect():
    current_user = getCurrentUser()
    if current_user in (anonymous, None):
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
    navbar = []
    for blueprint, prefix in current_app.config['MTJ_FLASK_NAV']:
        # XXX reintegrate this with mtj.flask.acl
        # permit = getBlueprintRole(blueprint)
        # if permit is None or permit in getCurrentUserRoles():
        #     navbar.append((blueprint, prefix))
        navbar.append((blueprint, prefix))

    set_json_root()
    g.navbar = navbar
    g.aclbar = [
        (getCurrentUser().login, '/acl/current'),
        ('logout', '/acl/logout'),
    ]

def set_json_root():
    json_prefix = current_app.config.get('MTJPOSTRACKER_JSON_PREFIX', 'json')
    # This is used by the javascript client.  Typically it is the same
    # instance as this.
    json_script_root = request.script_root
    # Alternatively a different one may be specified, but must be
    # accessible by the target end users.  This is for advanced usage.
    # XXX expose this at the config/runner level.
    # json_script_root = 'http://example.com/mtj.eve.tracker/frontend'
    g.json_root = json_script_root + json_prefix
