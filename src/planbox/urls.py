from django.conf.urls import patterns, include, url
from django.contrib import admin
import password_reset.urls
import planbox_data.urls
import planbox_ui.urls


admin.autodiscover()

def generate_error(request):
    raise Exception('Successfully failed.')

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'planbox.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^api/v1/', include(planbox_data.urls)),
    url(r'^generate-error$', generate_error),
    url(r'^shareabouts/create-dataset$', 'shareabouts_integration.views.create_dataset'),
    url(r'^', include(planbox_ui.urls)),
)
