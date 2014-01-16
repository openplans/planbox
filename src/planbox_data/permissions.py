from __future__ import unicode_literals

from rest_framework import permissions

from planbox_data import models


class IsOwnerOrReadOnly (permissions.BasePermission):
    def is_authed_as_owner(self, auth, obj):
        """
        Check whether the given authenticated user is the same same as the
        owner of the given object
        """
        if auth is None or obj is None:
            return False

        if not auth.is_authenticated():
            return False

        try:
            user = auth.planbox_user
        except models.User.DoesNotExist:
            user = None
        
        if user is None:
            return False

        return obj.owner == user

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return self.is_authed_as_owner(request.user, obj)
