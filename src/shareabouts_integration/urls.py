from django.conf.urls import patterns, url


urlpatterns = patterns('',
    url(r'^create-dataset$', 'shareabouts_integration.views.create_dataset'),
    url(r'^authorize-project$', 'shareabouts_integration.views.authorize_project'),
    url(r'^oauth-credentials$', 'shareabouts_integration.views.oauth_credentials'),
)