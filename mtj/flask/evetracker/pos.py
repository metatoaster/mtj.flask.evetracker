from __future__ import absolute_import

from flask import Blueprint, Flask, request, make_response, render_template


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


# Pos details

details = Blueprint('details', 'mtj.flask.evetracker.details')

@details.route('/')
def home_index():
    result = render_template('index.jinja')
    response = make_response(result)
    return response
