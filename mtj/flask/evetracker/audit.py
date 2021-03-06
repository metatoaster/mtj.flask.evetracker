import zope.component

from flask import Blueprint, Flask, request, g, make_response, render_template
from flask import flash, url_for, current_app, session, redirect, abort

from mtj.eve.tracker.interfaces import ITrackerBackend
from mtj.flask.acl.flask import permission_from_roles

audit = Blueprint('audit', 'mtj.flask.evetracker.audit.audit')

audit_viewer = permission_from_roles('audit_viewer')
raw_auditor = permission_from_roles('raw_auditor')
audit_writer = permission_from_roles('audit_writer')


@audit.route('/', defaults={'count': 50})
@audit.route('/<int:count>')
@audit_viewer.require()
def index(count):
    result = render_template('audit_index.jinja', count=count)
    response = make_response(result)
    return response

@audit.route('/add', methods=['GET', 'POST'])
@raw_auditor.require()
def add_audit_form():
    if request.method == 'GET':
        result = render_template('audit.jinja')
        response = make_response(result)
        return response

    backend = zope.component.getUtility(ITrackerBackend)
    table = request.form.get('table')
    rowid = request.form.get('rowid')
    reason = request.form.get('reason')
    category_name = request.form.get('category_name')
    user = current_app.config['MTJ_CURRENT_USER']()
    backend.addAudit((table, rowid), reason, user.login, category_name)
    result = render_template('audit.jinja')
    response = make_response(result)
    return response

@audit.route('/add/<table>/<int:rowid>', methods=['GET', 'POST'])
@audit_writer.require()
def add_audit_form_table_rowid(table, rowid):
    # TODO 404 on invalid table/rowids

    backend = zope.component.getUtility(ITrackerBackend)
    categories = backend.getAuditCategories(table)
    if not backend.getAuditable(table, rowid):
        abort(404);

    if request.method == 'GET':
        result = render_template('audit_table_id.jinja', categories=categories)
        response = make_response(result)
        return response

    reason = request.form.get('reason')
    category_name = request.form.get('category_name')
    user = current_app.config['MTJ_CURRENT_USER']()
    backend.addAudit((table, rowid), reason, user.login, category_name)
    # TODO redirect back to the actual entry.
    # XXX hardcoding redirect response here to tower only
    if table == 'tower':
        return redirect('%s/tower/%d' % (request.script_root, rowid))
    result = render_template('audit_table_id.jinja', categories=categories)
    response = make_response(result)
    return response

@audit.route('/view/<table>/<int:rowid>')
@audit_viewer.require()
def view_audit_table_rowid(table, rowid):
    # TODO 404 on invalid table/rowids

    backend = zope.component.getUtility(ITrackerBackend)
    categories = backend.getAuditCategories(table)
    if not backend.getAuditable(table, rowid):
        abort(404);

    result = render_template('audit_table_id_view.jinja',
        table=table, rowid=rowid)
    response = make_response(result)
    return response
