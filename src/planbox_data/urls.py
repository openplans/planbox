from django.conf.urls import patterns, url
from planbox_data import views

urlpatterns = views.router.urls + patterns('',
    url(r'projects/(?P<pk>[^/]+)/activity$', views.project_activity_view, name='project-activity')
)
