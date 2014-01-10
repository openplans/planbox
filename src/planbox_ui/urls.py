from django.conf.urls import patterns, url
from .views import app_view

urlpatterns = patterns('',
    url(r'^', app_view, name='app-demo'),
)
