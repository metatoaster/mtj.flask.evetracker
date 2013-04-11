from __future__ import absolute_import

from flask import Blueprint, Flask, request, g, make_response, render_template

from mtj.flask.evetracker import pos

app = Flask('mtj.flask.evetracker')

@app.before_request
def before_request():
    g.navbar = app.blueprints.keys()
    g.json_root = 'http://localhost:8000/json'

@app.teardown_request
def teardown_request(exception):
    pass

app.register_blueprint(pos.overview, url_prefix='/overview')
app.register_blueprint(pos.tower, url_prefix='/tower')


class ReverseProxied(object):
    '''Wrap the application in this middleware and configure the
    front-end server to add these headers, to let you quietly bind
    this to a URL other than / and to an HTTP scheme that is
    different than what is used locally.

    In nginx:
    location /myprefix {
        proxy_pass http://192.168.0.1:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Scheme $scheme;
        proxy_set_header X-Script-Name /myprefix;
        }

    :param app: the WSGI application

    In apache2:
    <Location /myprefix>
        ProxyPass http://localhost:5001
        ProxyPassReverse http://localhost:5001
        RequestHeader add X-Script-Name "/myprefix"
        RequestHeader add X-Scheme "http"
    </Location>

    Ensure both the mod_proxy and mod_headers are installed and enabled.
    '''
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        script_name = environ.get('HTTP_X_SCRIPT_NAME', '')
        if script_name:
            environ['SCRIPT_NAME'] = script_name
            path_info = environ['PATH_INFO']
            if path_info.startswith(script_name):
                environ['PATH_INFO'] = path_info[len(script_name):]

        scheme = environ.get('HTTP_X_SCHEME', '')
        if scheme:
            environ['wsgi.url_scheme'] = scheme
        return self.app(environ, start_response)


app.wsgi_app = ReverseProxied(app.wsgi_app)
