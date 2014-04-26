from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.shortcuts import redirect
import password_reset.urls
import planbox_data.urls
import planbox_ui.urls


admin.autodiscover()

def generate_error(request):
    raise Exception('Successfully failed.')

def redirect_to_blog(request, path=''):
    return redirect('http://blog.openplans.org/' + path, permanent=True)

def redirect_to_root(request):
    return redirect('app-index', permanent=True)

def redirect_to_team(request):
    return redirect('/about/#team', permanent=True)

def redirect_to_about(request):
    return redirect('app-about', permanent=True)

urlpatterns = patterns('',
    # Permanently redirect old URLs to new locations.
    url(r'^blog/?$', redirect_to_blog),
    url(r'^(author/.*/?)$', redirect_to_blog),
    url(r'^(category/.*/?)$', redirect_to_blog),
    url(r'^(\d{4}/\d{1,2}/.*)$', redirect_to_blog),
    url(r'^work/?$', redirect_to_root),
    url(r'^team_cpt/?$', redirect_to_team),
    url(r'^contact/?$', redirect_to_about),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^api/v1/', include(planbox_data.urls)),
    url(r'^generate-error$', generate_error),
    url(r'^', include(planbox_ui.urls)),
)
