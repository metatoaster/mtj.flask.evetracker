from __future__ import absolute_import

from flask import Blueprint, Flask, request, g, make_response, render_template


# template

home = Blueprint('home', 'mtj.flask.evetracker.home')
overview = Blueprint('overview', 'mtj.flask.evetracker.overview')
tower = Blueprint('towers', 'mtj.flask.evetracker.tower')

@home.route('/')
def home_index():
    result = render_template('index.jinja')
    response = make_response(result)
    return response

@overview.route('/')
def overview_index():
    result = render_template('overview.jinja')
    response = make_response(result)
    return response

@tower.route('/')
def tower_index():
    result = render_template('tower_list.jinja')
    response = make_response(result)
    return response

@tower.route('/<int:tower_id>')
def tower_id(tower_id):
    g.tower_id = tower_id
    result = render_template('tower.jinja', tower_id=tower_id)
    response = make_response(result)
    return response
