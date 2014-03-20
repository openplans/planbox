from __future__ import unicode_literals

from django.conf import settings
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User as UserAuth
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import redirect_to_login
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import resolve_url
from django.utils.decorators import method_decorator
from django.utils.http import is_safe_url
from django.views.generic import TemplateView, FormView
from planbox_data.models import Project, Profile
from planbox_data.serializers import ProjectSerializer, UserSerializer
from planbox_ui.decorators import ssl_required
from planbox_ui.forms import UserCreationForm
import pybars


def register_helper(helper_name):
    def _register(helper_callback):
        pybars._compiler._pybars_['helpers'][helper_name] = helper_callback
        return helper_callback
    return _register


class ReadOnlyMixin (object):
    http_method_names = ['get', 'head', 'options', 'trace']

    def get_context_data(self, **kwargs):
        return super(ReadOnlyMixin, self).get_context_data(read_only=True, **kwargs)


class AppMixin (object):
    def get_profile(self):
        if not hasattr(self, 'profile'):
            auth = self.request.user
            if auth.is_authenticated():
                try:
                    self.profile = auth.profile
                except Profile.DoesNotExist:
                    self.profile = None
            else:
                self.profile = None
        return self.profile

    def get_home_url(self, obj):
        if obj is None and self.request.user.is_authenticated():
            obj = self.request.user

        if isinstance(obj, UserAuth):
            owner_name = obj.username
        elif isinstance(obj, Profile):
            owner_name = obj.slug
        return resolve_url('app-new-project', owner_name=owner_name)

    def get_context_data(self, **kwargs):
        context = super(AppMixin, self).get_context_data(**kwargs)

        user_profile = self.get_profile()
        user_serializer = UserSerializer(user_profile)
        context['user_data'] = None if user_profile is None else user_serializer.data

        # Register handlebars helpers
        @register_helper('user')
        def user_attr_helper(this, attr):
            return context['user_data'].get(attr)

        @register_helper('window_location')
        def window_location_helper(this):
            return self.request.get_full_path()

        return context

class LoginRequired (object):
    def dispatch(self, request, *args, **kwargs):
        if self.get_profile() is None:
            path = request.get_full_path()
            return redirect_to_login(path)
        return super(LoginRequired, self).dispatch(request, *args, **kwargs)


class LogoutRequired (object):
    """
    Redirect a user to their profile home if they're already signed in
    """
    def dispatch(self, request, *args, **kwargs):
        profile = self.get_profile()
        if profile is not None:
            return redirect(self.get_home_url(profile))
        return super(LogoutRequired, self).dispatch(request, *args, **kwargs)


class SSLRequired (object):
    @method_decorator(ssl_required)
    def dispatch(self, request, *args, **kwargs):
        return super(SSLRequired, self).dispatch(request, *args, **kwargs)


# App
class IndexView (AppMixin, TemplateView):
    template_name = 'index.html'


class HelpView (AppMixin, TemplateView):
    template_name = 'help.html'


class SignupView (AppMixin, LogoutRequired, SSLRequired, FormView):
    template_name = 'signup.html'
    form_class = UserCreationForm

    def get_initial(self):
        initial = super(SignupView, self).get_initial()
        if 'email' in self.request.GET:
            initial['email'] = self.request.GET['email']
        return initial

    def get_success_url(self):
        return self.get_home_url(self.auth)

    def form_valid(self, form):
        form.save()
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        self.auth = authenticate(username=username, password=password)
        login(self.request, self.auth)
        return super(SignupView, self).form_valid(form)


class PasswordResetView (TemplateView):
    template_name = 'password-reset.html'


class SigninView (AppMixin, LogoutRequired, SSLRequired, FormView):
    template_name = 'signin.html'
    form_class = AuthenticationForm

    def get_context_data(self, **kwargs):
        if 'next' in self.request.GET:
            kwargs['next_url'] = self.request.GET['next']
        return super(SigninView, self).get_context_data(**kwargs)

    def get_success_url(self):
        # Ensure the user-originating redirection url is safe.
        redirect_to = self.request.REQUEST.get('next', self.get_home_url(self.auth))
        if not is_safe_url(url=redirect_to, host=self.request.get_host()):
            redirect_to = resolve_url(settings.LOGIN_REDIRECT_URL)
        return redirect_to

    def form_valid(self, form):
        # Okay, security check complete. Log the user in.
        self.auth = form.get_user()
        login(self.request, self.auth)
        return super(SigninView, self).form_valid(form)


class BaseProjectView (AppMixin, TemplateView):
    template_name = 'project.html'

    def get_context_data(self, **kwargs):
        context = super(BaseProjectView, self).get_context_data(**kwargs)

        project_serializer = ProjectSerializer(self.project)
        context['project'] = self.project
        context['project_data'] = project_serializer.data
        context['is_owner'] = self.project.owned_by(self.request.user) or self.request.user.is_superuser

        return context

    def get(self, request, owner_name, slug):
        self.project = get_object_or_404(Project.objects.select_related('theme'),
                                         owner__slug=owner_name, slug=slug)

        if not (request.user.is_superuser or self.project.public or self.project.owned_by(self.request.user)):
            raise Http404

        return super(BaseProjectView, self).get(request, pk=self.project.pk)


class ProjectView (SSLRequired, BaseProjectView): pass


class ReadOnlyProjectView (ReadOnlyMixin, BaseProjectView): pass


class NewProjectView (AppMixin, LoginRequired, SSLRequired, TemplateView):
    template_name = 'project.html'

    def get_context_data(self, **kwargs):
        context = super(NewProjectView, self).get_context_data(**kwargs)

        context['project_data'] = {}
        context['is_owner'] = True

        return context

    def get(self, request, owner_name):
        # Check whether this page is for the auth'd user
        if owner_name != request.user.username:
            return redirect('app-new-project', owner_name=self.request.user.username)

        owner_auth = get_object_or_404(UserAuth, username=owner_name)

        if 'force_new' not in request.GET:
            # Check whether the user has an existing project and redirect there.
            try:
                project = owner_auth.profile.projects.all()[0]
            except IndexError:
                pass
            else:
                return redirect('app-project', owner_name=owner_name, slug=project.slug)

        return super(NewProjectView, self).get(request, owner_name)


# SEO
class SiteMapView (AppMixin, TemplateView):
    template_name = 'sitemap.xml'

    def get_project_queryset(self):
        return Project.objects.filter(public=True).select_related('owner')

    def get_context_data(self, **kwargs):
        context = super(SiteMapView, self).get_context_data(**kwargs)
        context['projects'] = self.get_project_queryset()
        return context


# App views
index_view = IndexView.as_view()
project_view = ProjectView.as_view()
ro_project_view = ReadOnlyProjectView.as_view()
new_project_view = NewProjectView.as_view()
signup_view = SignupView.as_view()
signin_view = SigninView.as_view()
password_reset_view = PasswordResetView.as_view()
help_view = HelpView.as_view()
robots_view = TemplateView.as_view(template_name='robots.txt', content_type='text/plain')
sitemap_view = SiteMapView.as_view(content_type='text/xml')
