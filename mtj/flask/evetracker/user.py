from flask import Blueprint, Flask, request, g, make_response, render_template
from flask import flash, url_for, current_app, session, redirect

# TODO we should move this whole thing into a separate module.
from mtj.flask.evetracker import acl


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
    if acl_back.validate(login, password):
        session['logged_in'] = True
        flash('You were logged in')
        return redirect(request.script_root)
    else:
        error = 'Invalid credentials'

    result = render_template('login.jinja', error_msg=error)
    response = make_response(result)
    return response


@acl_front.route('/logout')
def logout():
    session.pop('logged_in', None)
    result = render_template('logout.jinja')
    response = make_response(result)
    return response
