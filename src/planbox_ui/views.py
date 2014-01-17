import json
from django.views.generic import TemplateView
from django.contrib.auth.models import User as AuthUser
from django.contrib.contenttypes.models import ContentType
from planbox_data.models import Project
from planbox_data.serializers import ProjectSerializer


# App
class IndexView (TemplateView):
    template_name = 'index.html'


class SignupView (TemplateView):
    template_name = 'signup.html'


class PasswordResetView (TemplateView):
    template_name = 'password-reset.html'


class SigninView (TemplateView):
    template_name = 'signin.html'


class ProjectView (TemplateView):
    template_name = 'project.html'

    def get_context_data(self, **kwargs):
        serializer = ProjectSerializer(self.project)
        context = super(ProjectView, self).get_context_data(**kwargs)
        context['project_data'] = json.dumps(serializer.data)
        return context

    def get(self, request, owner_name, slug):
        user_type = ContentType.objects.get(app_label='planbox_data', model='user')
        owner_auth = AuthUser.objects.get(username=owner_name)
        self.project = Project.objects.get(owner_type=user_type, owner_id=owner_auth.planbox_user.id, slug=slug)
        return super(ProjectView, self).get(request, owner_name, slug)


# App views
index_view = IndexView.as_view()
project_view = ProjectView.as_view()
signup_view = SignupView.as_view()
signin_view = SigninView.as_view()
password_reset_view = PasswordResetView.as_view()
