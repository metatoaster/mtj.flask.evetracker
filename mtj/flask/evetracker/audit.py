import zope.component

from flask import Blueprint, Flask, request, g, make_response, render_template
from flask import flash, url_for, current_app, session, redirect

from mtj.eve.tracker.interfaces import ITrackerBackend

audit = Blueprint('audit', 'mtj.flask.evetracker.audit.audit')


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
    backend.addAudit((table, rowid), reason, category_name, user)
    result = render_template('audit.jinja')
    response = make_response(result)
    return response
