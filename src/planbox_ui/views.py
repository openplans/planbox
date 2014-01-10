from django.views.generic import TemplateView


# App
class AppView (TemplateView):
    template_name = 'index.html'


# App views
app_view = AppView.as_view()
