from __future__ import unicode_literals

from django.http import HttpResponse
from django.utils.timezone import now
from rest_framework import response
from rest_framework import routers
from rest_framework import viewsets

from planbox_data import models
from planbox_data import serializers
from planbox_data import permissions


class ProfileViewSet (viewsets.ModelViewSet):
    serializer_class = serializers.ProfileSerializer
    permission_classes = (permissions.AuthedUserForUserProfile, permissions.TeamMemberForTeamProfile,)
    model = models.Profile

    def get_queryset(self):
        # For PUT/PATCH requests we need to refer to the complete set of
        # profiles to correctly identify the profile being updated. Otherwise
        # we may incorrectly assume that we are creating a new profile.
        if self.request.method.lower() in ('put', 'patch'):
            return models.Profile.objects.all()

        # For other requests, limit the queryset to those project to which the
        # user has access.
        user = self.request.user

        if user.is_superuser:
            return models.Profile.objects.all()

        if user.is_authenticated():
            return models.Profile.objects.filter_by_user_or_member(user)

        else:
            return models.Profile.objects.empty()


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

    def pre_save(self, obj):
        user = self.request.user
        obj.last_saved_by = user if user.is_authenticated() else None
        obj.last_saved_at = now()

    def notify_of_open(self, request, pk):
        self.project = self.get_object()
        user = self.project.get_opened_by()

        # If the current user is the last opening user, then save some
        # bandwidth and computation, and just return success with no
        # content (204).
        if user == request.user:
            self.project.mark_opened_by(request.user)
            return HttpResponse('', status=204)  # No Content

        serializer = serializers.ProjectActivitySerializer(self.project)

        # If there is no user with the project open, then mark it as opened by
        # the current user, and let them know.
        if user is None:
            self.project.mark_opened_by(request.user)
            return response.Response(serializer.data, status=200)

        # Otherwise, if the current user is not the one who last opened the
        # project, and they still have it open, return a conflict code (409).
        if user != request.user:
            return response.Response(serializer.data, status=409)  # Conflict

    def notify_of_close(self, request, pk):
        self.project = self.get_object()
        user = self.project.get_opened_by()

        serializer = serializers.ProjectActivitySerializer(self.project)

        # If the current user is the last opening user, then close them out.
        if user == request.user:
            self.project.mark_closed()
            return HttpResponse('', status=204)

        # Otherwise, respond with an invalid (400).
        else:
            return response.Response(serializer.data, status=400)  # Invalid


router = routers.DefaultRouter(trailing_slash=False)
router.register('profiles', ProfileViewSet)
router.register('projects', ProjectViewSet)

project_activity_view = ProjectViewSet.as_view({
    'post': 'notify_of_open',
    'delete': 'notify_of_close',
})
