from django.views.generic import TemplateView
from django.contrib.auth.models import User as AuthUser
from django.contrib.contenttypes.models import ContentType
from planbox_data.models import Project
from planbox_data.serializers import ProjectSerializer, UserSerializer


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
        context = super(ProjectView, self).get_context_data(**kwargs)

        if (self.request.user.is_authenticated()):
            user_serializer = UserSerializer(self.request.user.planbox_user)
            context['user_data'] = user_serializer.data
        else:
            context['user_data'] = None

        project_serializer = ProjectSerializer(self.project)

        context['project_data'] = project_serializer.data
        context['is_owner'] = self.project.owned_by(self.request.user)
        return context

    def get(self, request, owner_name, slug):
        user_type = ContentType.objects.get(app_label='planbox_data', model='user')
        owner_auth = AuthUser.objects.get(username=owner_name)
        self.project = Project.objects.get(owner_type=user_type, owner_id=owner_auth.planbox_user.id, slug=slug)
        return super(ProjectView, self).get(request, owner_name, slug)


class NewProjectView (TemplateView):
    template_name = 'project.html'

    def get_context_data(self, **kwargs):
        context = super(NewProjectView, self).get_context_data(**kwargs)

        user_serializer = UserSerializer(self.request.user.planbox_user)

        context['project_data'] = {}
        context['user_data'] = user_serializer.data
        context['is_owner'] = True
        return context

    def get(self, request, owner_name):
        # TODO: Decorate with @login_required
        # TODO: Set Andy's login page as the login page

        owner_auth = AuthUser.objects.get(username=owner_name)

        # Check whether the user has an existing project and redirect there.
        try:
            project = owner_auth.planbox_user.projects.all()[0]
        except IndexError:
            pass
        else:
            # TODO: Redirect
            pass

        return super(NewProjectView, self).get(request, owner_name)


# App views
index_view = IndexView.as_view()
project_view = ProjectView.as_view()
new_project_view = NewProjectView.as_view()
signup_view = SignupView.as_view()
signin_view = SigninView.as_view()
password_reset_view = PasswordResetView.as_view()
