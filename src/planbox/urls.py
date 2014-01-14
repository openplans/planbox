from django.conf.urls import patterns, include, url
from django.contrib import admin
import planbox_data.urls
import planbox_ui.urls


admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'planbox.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^api/', include(planbox_data.urls)),
    url(r'^', include(planbox_ui.urls)),
)
