from __future__ import absolute_import

from flask import Blueprint, Flask, request, g, make_response, render_template

from mtj.flask.evetracker.acl.flask import require_permit


# template

home = Blueprint('home', 'mtj.flask.evetracker.home')
overview = Blueprint('overview', 'mtj.flask.evetracker.overview')
tower = Blueprint('towers', 'mtj.flask.evetracker.tower')

@home.route('/')
@require_permit('pos_viewer')
def home_index():
    result = render_template('index.jinja')
    response = make_response(result)
    return response

@overview.route('/')
@require_permit('pos_viewer')
def overview_index():
    result = render_template('overview.jinja')
    response = make_response(result)
    return response

@tower.route('/')
@require_permit('pos_viewer')
def tower_index():
    result = render_template('tower_list.jinja')
    response = make_response(result)
    return response

@tower.route('/<int:tower_id>')
@require_permit('pos_viewer')
def tower_id(tower_id):
    g.tower_id = tower_id
    result = render_template('tower.jinja', tower_id=tower_id)
    response = make_response(result)
    return response
