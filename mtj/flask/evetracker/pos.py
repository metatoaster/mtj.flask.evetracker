from __future__ import absolute_import

from flask import Blueprint, Flask, request, g, make_response, render_template


# template

home = Blueprint('home', 'mtj.flask.evetracker.home')

@home.route('/')
def home_index():
    result = render_template('index.jinja')
    response = make_response(result)
    return response


# Overview.

overview = Blueprint('overview', 'mtj.flask.evetracker.overview')

@overview.route('/')
def overview_index():
    result = render_template('overview.jinja')
    response = make_response(result)
    return response


# Towers.

tower = Blueprint('tower', 'mtj.flask.evetracker.tower')

@tower.route('/')
def tower_overview_index():
    # TODO figure out how to share this with above overview?
    result = render_template('overview.jinja')
    response = make_response(result)
    return response

@tower.route('/<int:tower_id>')
def tower_index(tower_id):
    g.tower_id = tower_id
    result = render_template('tower.jinja')
    response = make_response(result)
    return response
