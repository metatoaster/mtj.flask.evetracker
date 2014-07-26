from __future__ import absolute_import

import zope.component
from flask import Blueprint, Flask, request, g, make_response, render_template
from flask import current_app

from mtj.f3u1.units import Time
from mtj.eve.tracker.interfaces import ITrackerBackend, ITowerManager

from mtj.flask.acl.flask import permission_from_roles


# template

home = Blueprint('home', 'mtj.flask.evetracker.home')
overview = Blueprint('overview', 'mtj.flask.evetracker.overview')
tower = Blueprint('towers', 'mtj.flask.evetracker.tower')

pos_viewer = permission_from_roles('pos_viewer')


@home.route('/')
@pos_viewer.require()
def home_index():
    result = render_template('index.jinja')
    response = make_response(result)
    return response

@overview.route('/')
@pos_viewer.require()
def overview_index():
    result = render_template('overview.jinja')
    response = make_response(result)
    return response

@overview.route('/strontium')
@overview.route('/strontium/<int:target_length>')
@pos_viewer.require()
def strontium_report(target_length=None):
    def getLabel(labels, tid):
        if labels.get(tid):
            return labels[tid][0].reason
        return ''

    if target_length is None:
        target_length = current_app.config.get('MTJ_DEFAULT_REINFORCE', 0)

    backend = zope.component.getUtility(ITrackerBackend)
    manager = zope.component.getUtility(ITowerManager)
    labels = backend.getAuditForTable('tower', category='label')

    att = [i for i in backend._towers.values()
        if backend.getTowerApiTimestamp(i.id)]
    towers = [{
            'id': tower.id,
            'state': tower.stateName,
            'label': getLabel(labels, tower.id),
            'region': tower.regionName,
            'celestial': tower.celestialName,
            'tower': tower.typeName,
            'currentLength': tower.getReinforcementLength(),
            'currentLengthFormatted': str(Time('hour',
                second=tower.getReinforcementLength())),
            'strontiumTarget': tower.getTargetStrontiumAmount(target_length),
            'strontiumDiff': tower.getTargetStrontiumDifference(target_length),
        } for tower in att if tower.state == 4 and
            tower.getReinforcementLength() != 3600 * target_length]

    result = render_template('strontium_report.jinja',
        target_length=target_length, towers=towers)
    response = make_response(result)
    return response

@tower.route('/')
@pos_viewer.require()
def tower_index():
    result = render_template('tower_list.jinja')
    response = make_response(result)
    return response

@tower.route('/<int:tower_id>')
@pos_viewer.require()
def tower_id(tower_id):
    g.tower_id = tower_id
    result = render_template('tower.jinja', tower_id=tower_id)
    response = make_response(result)
    return response
