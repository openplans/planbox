from __future__ import unicode_literals

from rest_framework import permissions

from planbox_data import models


class OwnerAuthorizesOrReadOnly (permissions.IsAuthenticatedOrReadOnly):
    def does_owner_authorize_access(self, user, project):
        """
        Check whether the given authenticated user is the same same as the
        owner of the given object
        """
        if user is None or project is None:
            return False

        if not user.is_authenticated():
            return False

        return project.owner.authorizes(user)

    def has_object_permission(self, request, view, project):
        if request.method in permissions.SAFE_METHODS:
            return True
        return self.does_owner_authorize_access(request.user, project)
