from flask import Blueprint, Flask, request, g, make_response, render_template
from flask import abort, flash, url_for, current_app, session, redirect

# TODO we should move this whole thing into a separate module.
from mtj.flask.evetracker import acl
anonymous = acl.anonymous

acl_front = Blueprint('acl_front', 'mtj.flask.evetracker.user.acl')


@acl_front.route('/login', methods=['GET', 'POST'])
def login():
    acl_back = current_app.config.get('MTJ_ACL')
    if not acl_back:
        # could use the flash method, but the session might not even be
        # available due to having no secret key set up.
        error_msg = 'Site not configured.'
        result = render_template('error.jinja', error_msg=error_msg)
        response = make_response(result)
        return response

    if request.method == 'GET':
        result = render_template('login.jinja')
        response = make_response(result)
        return response

    error = None
    login = request.form['login']
    password = request.form['password']
    user = acl_back.authenticate(login, password)

    if user:
        session['logged_in'] = current_app.config.get(
            'MTJ_LOGGED_IN', 'logged_in')
        session['mtj.user'] = user
        flash('Welcome %s' % user['login'])
        return redirect(request.script_root)
    else:
        error = 'Invalid credentials'

    result = render_template('login.jinja', error_msg=error)
    response = make_response(result)
    return response

@acl_front.route('/logout', methods=['GET', 'POST'])
def logout():
    if session.get('logged_in'):
        session.pop('logged_in', None)
        session.pop('mtj.user', None)
        # cripes bad way to display a message while ensuring the nav
        # elements for logged in users are not displayed.
        return redirect(url_for('acl_front.logout'))
    result = render_template('logout.jinja')
    response = make_response(result)
    return response

@acl_front.route('/current')
def current():
    result = render_template('user.jinja', user=getCurrentUser())
    response = make_response(result)
    return response

@acl_front.route('/list')
def list():
    verifyUserGroup('admin')
    acl_back = current_app.config.get('MTJ_ACL')
    users = acl_back.listUsers()
    result = render_template('user_list.jinja', users=users)
    response = make_response(result)
    return response


# helpers:

def getCurrentUser():
    access_token = session.get('mtj.user', {})
    acl_back = current_app.config.get('MTJ_ACL', None)
    if acl_back is None:
        return acl.anonymous
    return acl_back.getUserFromAccessToken(access_token)

def verifyUserGroup(group):
    user = getCurrentUser()
    acl_back = current_app.config.get('MTJ_ACL')
    if not group in acl_back.getUserGroups(user):
        abort(403)
