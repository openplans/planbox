from __future__ import unicode_literals

from django.conf.urls import patterns, url
from .views import (
    # Static site and metadata views
    index_view, about_view, shareabouts_view, open_source_view, help_view,
    robots_view, sitemap_view,

    # User authentication views
    signup_view, signin_view, password_reset_view, password_change_view,
    password_reset_request_view, password_reset_instructions_view,

    # Profile views
    profile_view,

    # Roundup views
    roundup_view,

    # Project views
    project_view, new_project_view, ro_project_view,
)

urlpatterns = patterns('',

    # Override the password change and reset views with ones that require SSL
    # and mixin with the app data.
    url(r'^change-password/$', password_change_view, name='password-change'),
    url(r'^reset-password/$', password_reset_request_view, name='password-reset-request'),
    url(r'^reset-password/instructions$', password_reset_instructions_view, name='password-reset-instructions'),
    url(r'^reset-password/(?P<token>[^/]*)$', password_reset_view, name='password-reset'),

    url(r'^signup/$', signup_view, name='app-signup'),
    url(r'^signin/$', signin_view, name='app-signin'),
    url(r'^signout/$', 'django.contrib.auth.views.logout', name='app-signout', kwargs={'next_page': '/'}),
    url(r'^help/$', help_view, name='app-help'),
    url(r'^robots.txt$', robots_view, name='app-robots'),
    url(r'^sitemap.xml$', sitemap_view, name='app-sitemap'),
    url(r'^$', index_view, name='app-index'),
    url(r'^about/$', about_view, name='app-about'),
    url(r'^shareabouts/$', shareabouts_view, name='app-shareabouts'),
    url(r'^open-source/$', open_source_view, name='app-open-source'),

    # ==============================
    # Profile dashboards

    url(r'^dashboard/', profile_view, name='app-user-profile'),
    url(r'^(?P<profile_slug>[^/]+)/dashboard/$', profile_view, name='app-profile'),

    # ==============================
    # Roundup pages

    url(r'^(?P<owner_slug>)[^/]+/$', roundup_view, name='app-roundup'),

    # ==============================
    # Project pages

    url(r'^(?P<owner_slug>[^/]+)/new/$', new_project_view, name='app-new-project'),
    url(r'^(?P<owner_slug>[^/]+)/(?P<project_slug>[^/]+)/edit/$', project_view, name='app-project'),
    # Read-only project page
    url(r'^(?P<owner_slug>[^/]+)/(?P<project_slug>[^/]+)/', ro_project_view, name='app-ro-project'),
)
