from __future__ import absolute_import

import functools

from flask import abort, current_app, session, request

from . import anonymous

# Flask helpers.

_permits = set()
_blueprint_permits = {}

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

def registerPermit(permit_name):
    _permits.add(permit_name)

def registerBlueprintPermit(blueprint, permit_name):
    # XXX blueprint needs to resolve to a name, but for now treat this
    # as a string.

    # one blueprint = one permit for now.
    if hasattr(blueprint, 'name'):  # blueprints have name
        blueprint = blueprint.name
    _blueprint_permits[blueprint] = permit_name
    registerPermit(permit_name)  # so it will be listed in getPermits

def getBlueprintPermit(blueprint):
    return _blueprint_permits.get(blueprint, None)

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

def verifyBlueprintPermit():
    blueprint_permit = getBlueprintPermit(request.blueprint)
    if blueprint_permit:
        verifyUserPermit(blueprint_permit)

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

    registerPermit(permit_name)

    def decorator(f):
        @functools.wraps(f)
        def wrapper(*a, **kw):
            verifyUserPermit(permit_name)
            return f(*a, **kw)
        return wrapper
    return decorator
