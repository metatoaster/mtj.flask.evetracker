from flask import Blueprint, Flask, request, g, make_response, render_template
from flask import abort, flash, url_for, current_app, session, redirect

# TODO we should move this whole thing into a separate module.
from mtj.flask.evetracker import acl
from mtj.flask.evetracker.acl.flask import *

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
    result = render_template('user.jinja', user=getCurrentUser(),
        group_names=getCurrentUserGroupNames())
    response = make_response(result)
    return response

@acl_front.route('/list')
@require_permit('admin')
def list():
    acl_back = current_app.config.get('MTJ_ACL')
    users = acl_back.listUsers()
    result = render_template('user_list.jinja', users=users)
    response = make_response(result)
    return response

@acl_front.route('/add', methods=['GET', 'POST'])
@require_permit('admin')
def add():
    acl_back = current_app.config.get('MTJ_ACL')

    if request.method == 'POST':
        login = request.form['login']
        password = request.form['password']
        name = request.form['name']
        email = request.form['email']
        result = acl_back.register(login, password, name, email)
        if result:
            flash('User created')
            return redirect(url_for('acl_front.edit', user_login=login))
        flash('Failed to create user %s as it already exists.' % login)

    result = render_template('user_add.jinja')
    response = make_response(result)
    return response

@acl_front.route('/edit/<user_login>', methods=['GET', 'POST'])
@require_permit('admin')
def edit(user_login):
    acl_back = current_app.config.get('MTJ_ACL')

    user = acl_back.getUser(user_login)
    if user is anonymous or user is None:
        # XXX catching both variations?
        abort(404)

    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        acl_back.editUser(user_login, name, email)
        flash('User updated')
        user = acl_back.getUser(user_login)

    result = render_template('user_edit.jinja', user=user)
    response = make_response(result)
    return response

@acl_front.route('/passwd', methods=['GET', 'POST'])
def passwd():
    acl_back = current_app.config.get('MTJ_ACL')
    result = error_msg = None
    user = getCurrentUser()

    if request.method == 'POST':
        old_password = request.form.get('old_password')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        # verification is done all the way through, but in reverse order
        if not (password and len(password) > 5):
            error_msg = 'New password too short.'
        if not password == confirm_password:
            error_msg = 'Password and confirmation password mismatched.'
        if not acl_back.validate(user.login, old_password):
            error_msg = 'Old password incorrect.'
        if not (old_password or password or confirm_password):
            error_msg = 'Please fill out all the required fields.'

        if not error_msg:
            result = acl_back.updatePassword(user.login, password)
            if result:
                flash('Password updated')
            else:
                error_msg = 'Error updating password.'

    result = render_template('user_passwd.jinja', user=user,
        error_msg=error_msg)
    response = make_response(result)
    return response


# Group Management

@acl_front.route('/group/list')
@require_permit('admin')
def group_list():
    acl_back = current_app.config.get('MTJ_ACL')
    groups = acl_back.listGroups()
    result = render_template('group_list.jinja', groups=groups)
    response = make_response(result)
    return response

@acl_front.route('/group/user/<user_login>', methods=['GET', 'POST'])
@require_permit('admin')
def group_user(user_login):
    acl_back = current_app.config.get('MTJ_ACL')
    error_msg = None

    user = acl_back.getUser(user_login)
    if user is anonymous or user is None:
        abort(404)

    if request.method == 'POST':
        acl_back.setUserGroups(user, request.form.getlist('group'))
        flash('Groups assigned to user.')
        return redirect(url_for('acl_front.group_user', user_login=user.login))

    all_groups = acl_back.listGroups()
    user_groups_names = [ug.name for ug in acl_back.getUserGroups(user)]

    result = render_template('group_user.jinja', user=user,
        user_groups_names=user_groups_names, all_groups=all_groups,
        error_msg=error_msg)
    response = make_response(result)
    return response
