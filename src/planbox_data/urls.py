from django.conf.urls import patterns, url
from planbox_data.views import router

urlpatterns = router.urls + patterns('',
)
