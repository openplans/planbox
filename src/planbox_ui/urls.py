from django.conf.urls import patterns, url
from .views import index_view, project_view, signup_view, signin_view, password_reset_view

urlpatterns = patterns('',

    url(r'^project/', project_view, name='app-project'),
    url(r'^signup/$', signup_view, name='app-signup'),
    url(r'^signin/$', signin_view, name='app-signin'),
    url(r'^password-reset/$', password_reset_view, name='app-password-reset'),
    url(r'^$', index_view, name='app-index'),
)
