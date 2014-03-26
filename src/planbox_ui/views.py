from __future__ import unicode_literals

import json
from django.conf import settings
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User as UserAuth
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import redirect_to_login
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import resolve_url
from django.utils.decorators import method_decorator
from django.utils.http import is_safe_url
from django.utils.timezone import now, timedelta
from django.views.generic import TemplateView, FormView, View
from planbox_data.models import Project, Profile
from planbox_data.serializers import ProjectSerializer, UserSerializer, TemplateProjectSerializer
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


class S3UploadMixin (object):
    DEFAULT_S3_UPLOAD_ACL = 'public-read'
    DEFAULT_S3_UPLOAD_EXP = timedelta(hours=1)

    def get_s3_upload_path(self):
        raise NotImplementedError('You must specify an S3 upload path')

    def get_s3_upload_success_url(self):
        url = reverse('app-s3-upload-success')
        return self.request.build_absolute_uri(url)

    def get_s3_upload_bucket(self):
        return settings.S3_MEDIA_BUCKET

    def get_s3_upload_acl(self):
        return self.DEFAULT_S3_UPLOAD_ACL

    def get_s3_upload_expiration(self):
        return (now() + self.DEFAULT_S3_UPLOAD_EXP).isoformat()

    def get_s3_upload_encoded_policy(self):
        policy_document = json.dumps({
            'expiration': self.get_s3_upload_expiration(),
            'conditions': [
                {'bucket': self.get_s3_upload_bucket()},
                {'acl': self.get_s3_upload_acl()},
                {'success_action_redirect': self.get_s3_upload_success_url()},
                ['starts-with', '$key', self.get_s3_upload_path()]
            ]
        })

        import base64
        policy = base64.b64encode(policy_document)
        return policy

    def get_s3_upload_signature(self, encoded_policy, aws_secret_key):
        """
        Constructs a secure token to upload directly to S3, using our upload
        policy and our secret access key. See the AWS documentation for more
        detail: http://aws.amazon.com/articles/1434#signyours3postform.
        """
        import base64, hmac, hashlib
        signature = base64.b64encode(hmac.new(aws_secret_key, encoded_policy, hashlib.sha1).digest())
        return signature

    def get_s3_upload_form_data(self):
        encoded_policy = self.get_s3_upload_encoded_policy()
        return {
            'key': '/'.join([self.get_s3_upload_path(), '${filename}']),
            'AWSAccessKeyId': settings.AWS_ACCESS_KEY,
            'acl': self.get_s3_upload_acl(),
            'success_action_redirect': self.get_s3_upload_success_url(),
            'policy': encoded_policy,
            'signature': self.get_s3_upload_signature(encoded_policy, settings.AWS_SECRET_KEY),
        }

    def get_context_data(self, **kwargs):
        context = super(S3UploadMixin, self).get_context_data(**kwargs)
        context['s3_upload_form_data'] = self.get_s3_upload_form_data()
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

    def get_project_serialized_data(self):
        project_serializer = ProjectSerializer(self.project)
        return project_serializer.data

    def get_project_is_owner(self):
        return self.project.owned_by(self.request.user) or self.request.user.is_superuser

    def get_context_data(self, **kwargs):
        context = super(BaseProjectView, self).get_context_data(**kwargs)

        context['project'] = self.project
        context['project_data'] = self.get_project_serialized_data()
        context['is_owner'] = self.get_project_is_owner()

        return context

    def get(self, request, owner_name, slug):
        self.project = get_object_or_404(Project.objects.select_related('theme', 'owner'),
                                         owner__slug=owner_name, slug=slug)

        if not (request.user.is_superuser or self.project.public or self.project.owned_by(self.request.user)):
            raise Http404

        return super(BaseProjectView, self).get(request, pk=self.project.pk)


class ProjectView (SSLRequired, S3UploadMixin, BaseProjectView):
    def get_s3_upload_path(self):
        owner_slug = self.kwargs['owner_name']
        project_slug = self.kwargs['slug']
        return '/'.join([owner_slug, project_slug])


class ReadOnlyProjectView (ReadOnlyMixin, BaseProjectView): pass


class NewProjectView (SSLRequired, LoginRequired, AppMixin, TemplateView):
    template_name = 'project.html'

    def get_template_project(self):
        request = self.request
        if 'template' in request.GET:
            template_string = request.GET['template']
        elif hasattr(settings, 'DEFAULT_PROJECT_TEMPLATE'):
            template_string = settings.DEFAULT_PROJECT_TEMPLATE
        else:
            return None

        try:
            owner_slug, project_slug = template_string.strip('/').split('/')
        except ValueError:
            return None

        try:
            project = Project.objects.get(owner__slug=owner_slug, slug=project_slug)
            return project
        except Project.DoesNotExist:
            return None


    def get_context_data(self, **kwargs):
        context = super(NewProjectView, self).get_context_data(**kwargs)

        project = self.get_template_project()
        if project:
            project.template = project
        serializer = TemplateProjectSerializer(project)
        context['project_data'] = serializer.data
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


# File Uploads
class S3FileUploadSuccess (AppMixin, View):
    def get(self, request):
        return HttpResponse(status_code=204)


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
s3_success_view = S3FileUploadSuccess.as_view()
