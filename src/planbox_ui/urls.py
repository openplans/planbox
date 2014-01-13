from django.conf.urls import patterns, url
from .views import index_view, project_view

urlpatterns = patterns('',

    url(r'^project/$', project_view, name='app-project'),
    url(r'^$', index_view, name='app-index'),
)
