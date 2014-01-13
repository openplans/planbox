from django.views.generic import TemplateView


# App
class IndexView (TemplateView):
    template_name = 'index.html'


class ProjectView (TemplateView):
    template_name = 'project.html'

# App views
index_view = IndexView.as_view()
project_view = ProjectView.as_view()
