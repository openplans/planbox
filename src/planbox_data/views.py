from __future__ import unicode_literals

from django.shortcuts import render
from rest_framework import routers
from rest_framework import viewsets

from planbox_data import models
from planbox_data import serializers


class ProjectViewSet (viewsets.ModelViewSet):
    serializer_class = serializers.ProjectSerializer
    queryset = models.Project.objects.all()


router = routers.DefaultRouter(trailing_slash=False)
router.register('projects', ProjectViewSet)