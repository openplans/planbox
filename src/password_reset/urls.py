from django.conf.urls import patterns, url
from password_reset.views import password_reset_view, password_reset_request_view, password_reset_instructions_view

urlpatterns = patterns('',
    url(r'^reset-password/$', password_reset_request_view, name='password-reset-request'),
    url(r'^reset-password/instructions$', password_reset_instructions_view, name='password-reset-instructions'),
    url(r'^reset-password/(?P<token>[^/]*)$', password_reset_view, name='password-reset'),
)
