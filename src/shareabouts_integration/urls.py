from django.conf.urls import patterns, url


urlpatterns = patterns('',
    url(r'^create-dataset$', 'shareabouts_integration.views.create_dataset'),
    url(r'^oauth-credentials$', 'shareabouts_integration.views.oauth_credentials'),
)