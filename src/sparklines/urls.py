from django.conf.urls import patterns, url
from sparklines.views import count_view, count_tsv

urlpatterns = patterns('',
    url(r'^(?P<app_label>[^/]+)/(?P<model>[^/]+)/count$', count_view, name='admin-model-count'),
    url(r'^(?P<app_label>[^/]+)/(?P<model>[^/]+)/count-data.tsv$', count_tsv, name='admin-model-count-data'),
)
