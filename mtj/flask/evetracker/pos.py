from __future__ import absolute_import

from flask import Blueprint, Flask, request, g, make_response, render_template


# template

home = Blueprint('home', 'mtj.flask.evetracker.home')
overview = Blueprint('overview', 'mtj.flask.evetracker.overview')
tower = Blueprint('tower', 'mtj.flask.evetracker.tower')

@home.route('/')
def home_index():
    result = render_template('index.jinja')
    response = make_response(result)
    return response


@tower.route('/')
@overview.route('/')  # right now overview shares this.
def overview_index():
    result = render_template('tower_list.jinja')
    response = make_response(result)
    return response


@tower.route('/<int:tower_id>')
def tower_index(tower_id):
    g.tower_id = tower_id
    result = render_template('tower.jinja')
    response = make_response(result)
    return response
