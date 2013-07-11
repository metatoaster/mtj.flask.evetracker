from __future__ import absolute_import

import functools

from flask import abort, current_app, session

from . import anonymous

# Flask helpers.

_permits = set()

def getCurrentUser():
    access_token = session.get('mtj.user', {})
    acl_back = current_app.config.get('MTJ_ACL', None)
    if acl_back is None:
        return anonymous
    return acl_back.getUserFromAccessToken(access_token)

def getCurrentUserGroupNames():
    user = getCurrentUser()
    acl_back = current_app.config.get('MTJ_ACL')
    return [gp.name for gp in acl_back.getUserGroups(user)]

def getCurrentUserPermits():
    user = getCurrentUser()
    acl_back = current_app.config.get('MTJ_ACL')
    if acl_back is None:
        return []
    return acl_back.getUserPermits(user)

def getPermits():
    return sorted(list(_permits))

def verifyUserGroupByName(group):
    if not group in getCurrentUserGroupNames():
        abort(403)
    return True

def verifyUserPermit(permit):
    acl_back = current_app.config.get('MTJ_ACL')
    if not permit in getCurrentUserPermits():
        if not current_app.config.get('MTJ_IGNORE_PERMIT'):
            abort(403)
    return True

def require_permit(permit_name):
    """
    A decorator for specifying the required permit to access the view
    this is decorated against.

    Permits are statically defined, and need to be hooked into groups
    which then can be freely customized and assigned with the rights to
    be granted.
    """

    # Add the permit into some global list for ease of assignment.
    # Ideally this should be within the app the function will ultimately
    # be accessed from, but that is impossible to determine so just
    # store the permit name into a global list available from within
    # this module.

    _permits.add(permit_name)

    def decorator(f):
        @functools.wraps(f)
        def wrapper(*a, **kw):
            verifyUserPermit(permit_name)
            return f(*a, **kw)
        return wrapper
    return decorator
