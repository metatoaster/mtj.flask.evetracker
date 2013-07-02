from __future__ import absolute_import

import functools

from flask import abort, current_app, session

from . import anonymous

# Flask helpers.

def getCurrentUser():
    access_token = session.get('mtj.user', {})
    acl_back = current_app.config.get('MTJ_ACL', None)
    if acl_back is None:
        return anonymous
    return acl_back.getUserFromAccessToken(access_token)

def verifyUserGroupByName(group):
    user = getCurrentUser()
    acl_back = current_app.config.get('MTJ_ACL')
    if not group in [gp.name for gp in acl_back.getUserGroups(user)]:
        abort(403)
    return True

def require_group(group_name):
    """
    A decorator around a raw view function.
    """

    def decorator(f):
        @functools.wraps(f)
        def wrapper(*a, **kw):
            verifyUserGroupByName(group_name)
            return f(*a, **kw)
        return wrapper
    return decorator
