from __future__ import unicode_literals

from rest_framework import routers
from rest_framework import viewsets

from planbox_data import models
from planbox_data import serializers
from planbox_data import permissions


class ProjectViewSet (viewsets.ModelViewSet):
    serializer_class = serializers.ProjectSerializer
    permission_classes = (permissions.OwnerAuthorizesOrReadOnly,)
    model = models.Project

    def get_queryset(self):
        # For PUT/PATCH requests we need to refer to the complete set of
        # projects to correctly identify the project being updated. Otherwise
        # we may incorrectly assume that we are creating a new project.
        if self.request.method.lower() in ('put', 'patch'):
            return models.Project.objects.all()

        # For other requests, limit the queryset to those project to whic the
        # user has access.
        user = self.request.user

        if user.is_superuser:
            return models.Project.objects.all()

        if user.is_authenticated():
            owner = self.request.user.profile
            return models.Project.objects.filter_by_member_or_public(owner)

        else:
            return models.Project.objects.filter(public=True)


router = routers.DefaultRouter(trailing_slash=False)
router.register('projects', ProjectViewSet)
