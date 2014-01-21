from __future__ import unicode_literals

from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User as AuthUser
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import resolve_url
from django.utils.decorators import method_decorator
from django.utils.http import is_safe_url
from django.views.generic import TemplateView, FormView, DetailView
from planbox_data.models import Project, User, Organization
from planbox_data.serializers import ProjectSerializer, UserSerializer


class LoginRequired (object):
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(LoginRequired, self).dispatch(request, *args, **kwargs)


# App
class IndexView (TemplateView):
    template_name = 'index.html'


class SignupView (TemplateView):
    template_name = 'signup.html'


class PasswordResetView (TemplateView):
    template_name = 'password-reset.html'


class SigninView (FormView):
    template_name = 'signin.html'
    form_class = AuthenticationForm

    def get_context_data(self, **kwargs):
        if 'next' in self.request.GET:
            kwargs['next_url'] = self.request.GET['next']
        return super(SigninView, self).get_context_data(**kwargs)

    def get_success_url(self):
        # Ensure the user-originating redirection url is safe.
        redirect_to = self.request.REQUEST.get('next', resolve_url('app-new-project', owner_name=self.username))
        if not is_safe_url(url=redirect_to, host=self.request.get_host()):
            redirect_to = resolve_url(settings.LOGIN_REDIRECT_URL)
        return redirect_to

    def form_valid(self, form):
        # Okay, security check complete. Log the user in.
        self.username = form.get_user()
        login(self.request, self.username)
        return super(SigninView, self).form_valid(form)


class ProjectView (TemplateView):
    template_name = 'project.html'

    def get_context_data(self, **kwargs):
        context = super(ProjectView, self).get_context_data(**kwargs)

        if (self.request.user.is_authenticated()):
            try:
                user_profile = self.request.user.planbox_profile
            except User.DoesNotExist:
                user_profile = None
        else:
            user_profile = None

        user_serializer = UserSerializer(user_profile)
        project_serializer = ProjectSerializer(self.project)

        context['user_data'] = None if user_profile is None else user_serializer.data
        context['project_data'] = project_serializer.data
        context['is_owner'] = self.project.owned_by(user_profile)

        return context

    def get(self, request, owner_name, slug):
        owner_types = ContentType.objects.get_for_models(User, Organization)

        try:
            owner = User.objects.get(auth__username=owner_name)
            owner_type = owner_types[User]
        except User.DoesNotExist:
            owner = get_object_or_404(Organization, name=owner_name)
            owner_type = owner_types[Organization]

        self.project = get_object_or_404(Project, owner_type=owner_type, owner_id=owner.pk, slug=slug)
        return super(ProjectView, self).get(request, pk=self.project.pk)


class NewProjectView (LoginRequired, TemplateView):
    template_name = 'project.html'

    def get_context_data(self, **kwargs):
        context = super(NewProjectView, self).get_context_data(**kwargs)

        user_serializer = UserSerializer(self.request.user.planbox_profile)
        context['project_data'] = {}
        context['user_data'] = user_serializer.data
        context['is_owner'] = True

        return context

    def get(self, request, owner_name):
        # Check whether this page is for the auth'd user
        if owner_name != request.user.username:
            return redirect('app-new-project', owner_name=self.request.user.username)

        owner_auth = get_object_or_404(AuthUser, username=owner_name)

        if 'force_new' not in request.GET:
            # Check whether the user has an existing project and redirect there.
            try:
                project = owner_auth.planbox_profile.projects.all()[0]
            except IndexError:
                pass
            else:
                return redirect('app-project', owner_name=owner_name, slug=project.slug)

        return super(NewProjectView, self).get(request, owner_name)


# App views
index_view = IndexView.as_view()
project_view = ProjectView.as_view()
new_project_view = NewProjectView.as_view()
signup_view = SignupView.as_view()
signin_view = SigninView.as_view()
password_reset_view = PasswordResetView.as_view()
