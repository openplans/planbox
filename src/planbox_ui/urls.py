from __future__ import unicode_literals

from django.conf.urls import patterns, url
from .views import index_view, project_view, new_project_view, signup_view, signin_view, password_reset_view, help_view, robots_view, sitemap_view, ro_project_view, profile_view

urlpatterns = patterns('',

    # Read-only resources
    url(r'^~/(?P<owner_name>[^/]+)/(?P<slug>[^/]+)/', ro_project_view, name='app-ro-project'),

    # Creating a new project
    url(r'^(?P<owner_name>[^/]+)/new/', new_project_view, name='app-new-project'),

    # Read-write version of the project page
    url(r'^(?P<owner_name>[^/]+)/(?P<slug>[^/]+)/', project_view, name='app-project'),

    # Read-write version of the project page
    url(r'^profile/', profile_view, name='app-profile'),

    url(r'^signup/$', signup_view, name='app-signup'),
    url(r'^signin/$', signin_view, name='app-signin'),
    url(r'^signout/$', 'django.contrib.auth.views.logout', name='app-signout', kwargs={'next_page': '/'}),
    url(r'^help/$', help_view, name='app-help'),
    url(r'^robots.txt$', robots_view, name='app-robots'),
    url(r'^sitemap.xml$', sitemap_view, name='app-sitemap'),
    url(r'^$', index_view, name='app-index'),
)
