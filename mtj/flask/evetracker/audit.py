import zope.component

from flask import Blueprint, Flask, request, g, make_response, render_template
from flask import flash, url_for, current_app, session, redirect, abort

from mtj.eve.tracker.interfaces import ITrackerBackend

audit = Blueprint('audit', 'mtj.flask.evetracker.audit.audit')


@audit.route('/')
def index():
    result = render_template('audit_index.jinja')
    response = make_response(result)
    return response

@audit.route('/add', methods=['GET', 'POST'])
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
    backend.addAudit((table, rowid), reason, user, category_name)
    result = render_template('audit.jinja')
    response = make_response(result)
    return response

@audit.route('/add/<table>/<int:rowid>', methods=['GET', 'POST'])
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
    backend.addAudit((table, rowid), reason, user, category_name)
    # TODO redirect back to the actual entry.
    # XXX hardcoding redirect response here to tower only
    if table == 'tower':
        return redirect('%s/tower/%d' % (request.script_root, rowid))
    result = render_template('audit_table_id.jinja', categories=categories)
    response = make_response(result)
    return response

@audit.route('/view/<table>/<int:rowid>')
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
