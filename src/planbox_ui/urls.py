from __future__ import unicode_literals

from django.conf.urls import patterns, url
from .views import index_view, project_view, new_project_view, signup_view, signin_view, password_reset_view

urlpatterns = patterns('',

    url(r'^(?P<owner_name>[^/]+)/new', new_project_view, name='app-new-project'),
    url(r'^(?P<owner_name>[^/]+)/(?P<slug>[^/]+)/', project_view, name='app-project'),
    url(r'^signup/$', signup_view, name='app-signup'),
    url(r'^signin/$', signin_view, name='app-signin'),
    url(r'^password-reset/$', password_reset_view, name='app-password-reset'),
    url(r'^$', index_view, name='app-index'),
)
