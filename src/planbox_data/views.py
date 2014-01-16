from __future__ import unicode_literals

from rest_framework import routers
from rest_framework import viewsets

from planbox_data import models
from planbox_data import serializers
from planbox_data import permissions


class ProjectViewSet (viewsets.ModelViewSet):
    serializer_class = serializers.ProjectSerializer
    queryset = models.Project.objects.all()
    permission_classes = (permissions.IsOwnerOrReadOnly,)


router = routers.DefaultRouter(trailing_slash=False)
router.register('projects', ProjectViewSet)