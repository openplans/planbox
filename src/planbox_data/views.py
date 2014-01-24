from __future__ import unicode_literals

from rest_framework import routers
from rest_framework import viewsets

from planbox_data import models
from planbox_data import serializers
from planbox_data import permissions


class ProjectViewSet (viewsets.ModelViewSet):
    serializer_class = serializers.ProjectSerializer
    permission_classes = (permissions.IsOwnerOrReadOnly,)
    model = models.Project

    def get_queryset(self):
        user = self.request.user

        if user.is_superuser:
            return models.Project.objects.all()

        if user.is_authenticated():
            owner = self.request.user.profile
            return models.Project.objects.filter_by_owner_or_public(owner)

        else:
            return models.Project.objects.filter(public=True)


router = routers.DefaultRouter(trailing_slash=False)
router.register('projects', ProjectViewSet)