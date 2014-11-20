from __future__ import unicode_literals

import base64
import hmac
import hashlib
import json
import requests
from datetime import datetime, timedelta
from django.conf import settings
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User as UserAuth
from django.contrib.auth.views import redirect_to_login
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import resolve_url
from django.template import Context, Template
from django.utils.decorators import method_decorator
from django.utils.http import is_safe_url
from django.utils.timezone import now
from django.views.generic import TemplateView, FormView, View, DetailView
from moonclerk.models import Customer, Payment
from password_reset.views import (
    PasswordResetView as BasePasswordResetView,
    PasswordResetRequestView as BasePasswordResetRequestView,
    PasswordResetInstructionsView as BasePasswordResetInstructionsView,
    PasswordChangeView as BasePasswordChangeView)
from planbox_data.models import Project, Profile, Roundup
from planbox_data.serializers import (ProjectSerializer, UserSerializer,
    FullProjectSerializer, RoundupSerializer, ProfileProjectTemplateSerializer,
    TemplateProjectSerializer, ProfileSerializer, ProjectActivitySerializer)
from planbox_ui.decorators import ssl_required
from planbox_ui.forms import UserCreationForm, AuthenticationForm
import pybars

import logging
log = logging.getLogger(__name__)

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
    def get_user_profile(self):
        if not hasattr(self, 'user_profile'):
            auth = self.request.user
            if auth.is_authenticated():
                try:
                    self.user_profile = auth.profile
                except Profile.DoesNotExist:
                    self.user_profile = None
            else:
                self.user_profile = None
        return self.user_profile

    def get_home_url(self, obj=None):
        if obj is None:
            profile = self.get_user_profile()
        elif hasattr(obj, 'profile'):
            profile = obj.profile
        else:
            profile = obj

        if profile and profile.teams.all().count() == 1:
            return resolve_url('app-profile', profile_slug=profile.teams.all()[0].slug)
        else:
            return resolve_url('app-user-profile')

    def get_context_data(self, **kwargs):
        context = super(AppMixin, self).get_context_data(**kwargs)

        user_profile = self.get_user_profile()
        user_serializer = UserSerializer(user_profile)
        user_data = None if user_profile is None else user_serializer.data
        context['user_data'] = user_data

        # intercom secure mode
        if hasattr(settings, 'INTERCOM_SECRET') and user_data:
            context['intercom_user_hash'] = hmac.new(settings.INTERCOM_SECRET,
                user_data['username'], digestmod=hashlib.sha256).hexdigest()

        # Register handlebars helpers
        @register_helper('user')
        def user_attr_helper(this, attr):
            user_data = context.get('user_data', None)
            if user_data is not None:
                return user_data.get(attr)
            else:
                return None

        @register_helper('window_location')
        def window_location_helper(this):
            return self.request.get_full_path()

        # The current time, because it's useful sometimes
        context['current_time'] = now()

        return context


class AlwaysFresh (object):
    """
    Disallow client-side caching so that stale data isn't kept (e.g., when the
    user presses the back button).
    """
    def get(self, request, *args, **kwargs):
        response = super(AlwaysFresh, self).get(request, *args, **kwargs)
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response['Pragma'] = 'no-cache'
        response['Expires'] = 0
        return response


class S3UploadMixin (object):
    DEFAULT_S3_UPLOAD_ACL = 'public-read'
    DEFAULT_S3_UPLOAD_EXP = timedelta(hours=1)

    def get_s3_upload_path(self):
        try:
            return super(S3UploadMixin, self).get_s3_upload_path()
        except AttributeError:
            raise NotImplementedError('You must specify an S3 upload path')

    def get_s3_upload_bucket(self):
        return settings.S3_MEDIA_BUCKET

    def get_s3_upload_acl(self):
        return self.DEFAULT_S3_UPLOAD_ACL

    def get_s3_upload_expiration(self):
        format = '%Y-%m-%dT%H:%M:%SZ'
        return (datetime.utcnow() + self.DEFAULT_S3_UPLOAD_EXP).strftime(format)

    def get_s3_upload_encoded_policy(self):
        policy_document = json.dumps({
            'expiration': self.get_s3_upload_expiration(),
            'conditions': [
                {'bucket': self.get_s3_upload_bucket()},
                {'acl': self.get_s3_upload_acl()},
                ['starts-with', '$key', self.get_s3_upload_path()],
                ['starts-with', '$Content-Type', ''],
            ]
        })

        policy_bytes = policy_document.encode('utf-8')
        policy = base64.b64encode(policy_bytes)
        return policy

    def get_s3_upload_signature(self, encoded_policy, aws_secret_key):
        """
        Constructs a secure token to upload directly to S3, using our upload
        policy and our secret access key. See the AWS documentation for more
        detail: http://aws.amazon.com/articles/1434#signyours3postform.
        """
        key_bytes = aws_secret_key.encode('utf-8')
        signature = base64.b64encode(hmac.new(key_bytes, encoded_policy, hashlib.sha1).digest())
        return signature

    def get_s3_upload_form_data(self):
        encoded_policy = self.get_s3_upload_encoded_policy()
        upload_signature = self.get_s3_upload_signature(encoded_policy, settings.AWS_SECRET_KEY)
        return {
            'key': '/'.join([self.get_s3_upload_path(), '${filename}']),
            'AWSAccessKeyId': settings.AWS_ACCESS_KEY,
            'acl': self.get_s3_upload_acl(),
            'policy': encoded_policy.decode('utf-8'),
            'signature': upload_signature.decode('utf-8'),
        }

    def get_context_data(self, **kwargs):
        context = super(S3UploadMixin, self).get_context_data(**kwargs)
        context['s3_upload_form_data'] = self.get_s3_upload_form_data()
        return context


class LoginRequired (object):
    def dispatch(self, request, *args, **kwargs):
        if self.get_user_profile() is None:
            path = request.get_full_path()
            return redirect_to_login(path)
        return super(LoginRequired, self).dispatch(request, *args, **kwargs)


class LogoutRequired (object):
    """
    Redirect a user to their profile home if they're already signed in
    """
    def dispatch(self, request, *args, **kwargs):
        profile = self.get_user_profile()
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

class AboutView (AppMixin, TemplateView):
    template_name = 'about.html'

class ShareaboutsView (AppMixin, TemplateView):
    template_name = 'shareabouts.html'

class ShareaboutsAuthSuccessView (AppMixin, TemplateView):
    template_name = 'shareabouts/auth-success.html'

class ShareaboutsAuthErrorView (AppMixin, TemplateView):
    template_name = 'shareabouts/auth-error.html'

class OpenSourceView (AppMixin, TemplateView):
    template_name = 'open-source.html'

class MapFlavorsView (AppMixin, TemplateView):
    template_name = 'map-flavors.html'

class ProjectFlavorView (AppMixin, TemplateView):
    template_name = 'flavor.html'

    def get_context_data(self, **kwargs):
        context = super(ProjectFlavorView, self).get_context_data(**kwargs)
        context['details'] = self.render_flavor_details(context)
        return context

    def get_flavor_details_template(self, slug):
        flavor_base_url = '%s/%s/' % (settings.PLANBOX_FLAVORS_ROOT_URL.strip('/'), slug)
        response = requests.get(flavor_base_url + 'details.html')
        if response.status_code == 200:
            return Template(response.text)
        elif response.status_code == 404:
            raise Http404
        else:
            raise Exception('Invalid response while retrieving flavor details: %s %s' % (response.status_code, response.content))

    def render_flavor_details(self, context_data):
        details_context = Context(context_data)
        return self.details_template.render(details_context)

    def get(self, request, slug):
        self.details_template = self.get_flavor_details_template(slug)
        return super(ProjectFlavorView, self).get(request, slug)

class ExpiredProjectView (AppMixin, TemplateView):
    template_name = 'plan-expired.html'

class HelpView (AppMixin, TemplateView):
    template_name = 'help.html'


class PasswordChangeView (AppMixin, LoginRequired, SSLRequired, BasePasswordChangeView): pass
class PasswordResetView (AppMixin, SSLRequired, BasePasswordResetView): pass
class PasswordResetRequestView (AppMixin, SSLRequired, BasePasswordResetRequestView): pass
class PasswordResetInstructionsView (AppMixin, SSLRequired, BasePasswordResetInstructionsView): pass


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

    def get_template_project(self):
        if hasattr(settings, 'PLANBOX_STARTER_PROJECT_TEMPLATE'):
            template_string = settings.PLANBOX_STARTER_PROJECT_TEMPLATE
        else:
            return None

        try:
            owner_slug, project_slug = template_string.strip('/').split('/')
        except (AttributeError, ValueError):
            return None

        try:
            project = Project.objects.get(owner__slug=owner_slug, slug=project_slug)
            return project
        except Project.DoesNotExist:
            return None

    def form_valid(self, form):
        template = self.get_template_project()
        form.save(starter_template=template)

        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        self.auth = authenticate(username=username, password=password)
        login(self.request, self.auth)
        return super(SignupView, self).form_valid(form)


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


class ProfileView (AppMixin, AlwaysFresh, LoginRequired, SSLRequired, S3UploadMixin, TemplateView):
    template_name = 'profile-admin.html'

    def get_profile(self, request, profile_slug):
        if profile_slug:
            return get_object_or_404(Profile.objects.filter(auth=None), slug=profile_slug)
        else:
            try:
                return request.user.profile
            except Profile.DoesNotExist:
                return None

    def get_s3_upload_path(self):
        slug = self.kwargs.get('profile_slug', self.profile.slug)
        return slug

    def get_context_data(self, **kwargs):
        context = super(ProfileView, self).get_context_data(**kwargs)

        # The profile model
        context['profile'] = self.profile

        # The serialized representation of the profile. This is used to
        # construct the admin view.
        serializer = ProfileSerializer(self.profile)
        context['profile_data'] = serializer.data

        # The project templates
        ### TODO: Cache these
        templates_slug = settings.TEMPLATES_PROFILE
        templates = Profile.objects.get(slug=templates_slug)
        project_templates_serializer = ProfileProjectTemplateSerializer(templates.project_templates.all(), many=True)
        context['project_templates_data'] = project_templates_serializer.data

        return context

    def get(self, request, profile_slug=None):
        # Save the profile on the view
        self.profile = self.get_profile(request, profile_slug)
        if self.profile is None:
            log.error('User "%s" has no profile' % (request.user,),
                      extra={'stack': True})
            return redirect('app-index')

        # Check for authorization on the profile
        if not self.profile.authorizes(request.user):
            return redirect('app-index')

        # If authorized, proceed
        return super(ProfileView, self).get(request, profile_slug=profile_slug)


class ProjectMixin (AppMixin):
    def get_owner_profile(self):
        if not hasattr(self, 'owner_profile'):
            try:
                self.owner_profile = self.project.owner
            except (Profile.DoesNotExist, AttributeError):  # AttributeError if project is None`
                try:
                    self.owner_profile = Profile.objects.get(slug=self.kwargs.get('owner_slug'))
                except Profile.DoesNotExist:
                    self.owner_profile = None
        return self.owner_profile

    def get_context_data(self, **kwargs):
        context = super(ProjectMixin, self).get_context_data(**kwargs)

        # The project model on which we are currently operating (maybe None)
        context['project'] = self.project

        # The project owner (maybe None)
        owner_profile = self.get_owner_profile()
        owner_serializer = UserSerializer(owner_profile)
        owner_data = None if owner_profile is None else owner_serializer.data
        context['owner_data'] = owner_data

        # The serialized representation of the project. This is used to
        # construct the project page for edit and/or display.
        context['project_data'] = self.get_project_serialized_data()

        # A flag denoting whether the current user is the project owner. Used
        # to determine whether an editable interface should be presented.
        is_editable = self.get_project_is_editable()
        context['is_editable'] = is_editable

        if self.project and is_editable and not self.project.is_opened_by(self.request.user):
            activity_serializer = ProjectActivitySerializer(self.project)
            activity_data = activity_serializer.data
            context['activity_data'] = activity_data
        else:
            context['activity_data'] = None

        return context


class BaseExistingProjectView (AlwaysFresh, ProjectMixin, TemplateView):
    def get_project_is_visible(self):
        return (
            self.request.user.is_superuser or
            self.project.public or
            self.project.editable_by(self.request.user)
        )

    def get_project_serialized_data(self):
        project_serializer = ProjectSerializer(self.project)
        return project_serializer.data

    def get_s3_upload_path(self):
        owner_slug = self.kwargs['owner_slug']
        project_slug = self.kwargs['project_slug']
        return '/'.join([owner_slug, project_slug])

    def is_project_open(self):
        return self.project.get_opened_by()

    def is_project_active(self):
        return (
            self.project.expires_at is None or
            now() < self.project.expires_at
        )


class ProjectEditorView (SSLRequired, LoginRequired, S3UploadMixin, BaseExistingProjectView):
    """
    A view on an existing project that presents an editable template when the
    authenticated user is the owner of the project.
    """

    template_name = 'project-admin.html'

    def get_project_serialized_data(self):
        project_serializer = FullProjectSerializer(self.project)
        return project_serializer.data

    def get_project_is_editable(self):
        return self.project.editable_by(self.request.user)

    def get_s3_upload_form_data(self):
        if self.get_project_is_editable():
            return super(ProjectEditorView, self).get_s3_upload_form_data()
        else:
            return None

    def get_template_names(self):
        if not self.is_project_active():
            return ['project-expired.html']
        return super(ProjectEditorView, self).get_template_names()

    def get(self, request, owner_slug, project_slug):
        self.project = get_object_or_404(Project.objects.select_related('theme', 'owner'),
                                         owner__slug=owner_slug, slug__iexact=project_slug)

        if not self.get_project_is_editable():
            raise Http404

        if not self.is_project_active():
            context = self.get_context_data(**self.kwargs)
            return self.render_to_response(context, status=402)

        if not self.is_project_open():
            self.project.mark_opened_by(request.user)

        return super(ProjectEditorView, self).get(request, pk=self.project.pk)


class ProjectPaymentsView (SSLRequired, LoginRequired, BaseExistingProjectView):
    """
    A view on an existing project that allows users to make payments.
    """

    def get_project_is_editable(self):
        return False

    def get_template_names(self):
        return ['project-payment.html']

    def get_project_token(self):
        project_token = self.project.id
        return project_token

    def get_context_data(self, **kwargs):
        context = super(ProjectPaymentsView, self).get_context_data(**kwargs)
        project_token = self.get_project_token()
        project_token_path = reverse('app-project-payments-success', kwargs={'pk': project_token})
        context['project_token'] = project_token
        context['project_token_url'] = self.request.build_absolute_uri(project_token_path)
        return context

    def get(self, request, owner_slug, project_slug):
        self.project = get_object_or_404(Project.objects.select_related('theme', 'owner'),
                                         owner__slug=owner_slug, slug__iexact=project_slug)
        return super(ProjectPaymentsView, self).get(request, pk=self.project.pk)


class ProjectPaymentsSuccessView (SSLRequired, LoginRequired, AppMixin, DetailView):
    def get_moonclerk_customer(self, request, customer_id, moonclerk_key):
        url = 'https://api.moonclerk.com/customers/%s' % (customer_id,)
        headers = {'Authorization': 'Token token=%s' % (moonclerk_key,),
                   'Accept': 'application/vnd.moonclerk+json;version=1'}

        try:
            response = requests.get(url, headers=headers, timeout=15)
        except:  # Socket timeout, or other such connection errors
            raise Exception('Failed to connect to the MookClerk API')

        if response.status_code != 200:
            response_body = response.text
            raise Exception('Invalid response from the MoonClerk API')

        customer_data = response.json()
        customer = Customer.objects.create(
            user=request.user,
            reference=customer_data.get('customer', {}).get('customer_reference'),
            customer_id=customer_id,
            data=customer_data)
        return customer

    def get_moonclerk_payment(self, request, payment_id, moonclerk_key):
        url = 'https://api.moonclerk.com/payments/%s' % (payment_id,)
        headers = {'Authorization': 'Token token=%s' % (moonclerk_key,),
                   'Accept': 'application/vnd.moonclerk+json;version=1'}

        try:
            response = requests.get(url, headers=headers, timeout=15)
        except:  # Socket timeout, or other such connection errors
            raise Exception('Failed to connect to the MookClerk API')

        if response.status_code != 200:
            response_body = response.text
            raise Exception('Invalid response from the MoonClerk API')

        payment_data = response.json()
        payment = Payment.objects.create(
            user=request.user,
            payment_id=payment_id,
            data=payment_data)
        return payment

    def set_payment_info(self, project, payment, customer):
        if payment and payment.customer_id is None:
            project.payment_type = 'moonclerk-onetime'
        else:
            project.payment_type = 'moonclerk-monthly'

        if customer:
            project.customer = customer
        if payment:
            project.payments.add(payment)

        project.expires_at = None
        project.save()

    def get_payment_error(self):
        self.template_name = 'payment-error.html'
        context = self.get_context_data()
        return self.render_to_response(context, status=500)

    def get(self, request, pk):
        self.object = project = get_object_or_404(Project.objects.select_related('owner'), pk=pk)
        moonclerk_key = settings.MOONCLERK_API_KEY

        customer_id = request.GET.get('customer_id', None)
        payment_id = request.GET.get('payment_id', None)

        if customer_id is None and payment_id is None:
            return HttpResponse('You must specify either a customer_id or a payment_id.', status=400)

        payment = customer = None
        try:
            if customer_id:
                customer = self.get_moonclerk_customer(request, customer_id, moonclerk_key)
            if payment_id:
                payment = self.get_moonclerk_payment(request, payment_id, moonclerk_key)
            assert customer or payment
        except:
            # Something went wrong and we weren't able to create a customer or
            # payment.
            from raven.contrib.django.models import client
            client.captureException()
            return self.get_payment_error()

        self.set_payment_info(project, payment, customer)

        return redirect('app-project-activation-success',
            owner_slug=project.owner.slug,
            project_slug=project.slug)


class ProjectActivationSuccessView (SSLRequired, LoginRequired, AppMixin, TemplateView):
    template_name = 'payment-success.html'

    def get_context_data(self, **kwargs):
        context = super(ProjectActivationSuccessView, self).get_context_data(**kwargs)
        context['project'] = self.project
        return context

    def get(self, request, owner_slug, project_slug):
        self.project = get_object_or_404(Project.objects.select_related('theme', 'owner'),
                                         owner__slug=owner_slug, slug__iexact=project_slug)
        return super(ProjectActivationSuccessView, self).get(request, pk=self.project.pk)


class ProjectPageView (ReadOnlyMixin, BaseExistingProjectView):
    """
    A view on an existing project where that always presumes the user is NOT
    the project owner (thus it is always in read-only mode).
    """

    template_name = 'project.html'

    def get_project_is_editable(self):
        return False

    def get(self, request, owner_slug, project_slug):
        self.project = get_object_or_404(Project.objects.select_related('theme', 'owner'),
                                         owner__slug=owner_slug, slug__iexact=project_slug)

        if not self.is_project_active():
            raise Http404

        if not self.get_project_is_visible():
            raise Http404

        return super(ProjectPageView, self).get(request, pk=self.project.pk)


class ProjectDashboardView (SSLRequired, LoginRequired, BaseExistingProjectView):
    """
    A view on an existing project where that always presumes the user is NOT
    the project owner (thus it is always in read-only mode).
    """

    template_name = 'project-dashboard.html'

    def get_project_is_editable(self):
        return self.project.editable_by(self.request.user)

    def get_template_names(self):
        if not self.is_project_active():
            return ['project-expired.html']
        return super(ProjectDashboardView, self).get_template_names()

    def get(self, request, owner_slug, project_slug):
        self.project = get_object_or_404(Project.objects.select_related('theme', 'owner'),
                                         owner__slug=owner_slug, slug__iexact=project_slug)

        if not self.get_project_is_editable():
            raise Http404

        return super(ProjectDashboardView, self).get(request, pk=self.project.pk)


class NewProjectView (SSLRequired, LoginRequired, S3UploadMixin, ProjectMixin, TemplateView):
    """
    A project view for a project that does not yet exist. The project
    attribute is always None for objects of this class. A template project
    may be specified, which the view will render with a template project
    serializer, which strips any identifying information (ids, slugs, etc.)
    from the project data.

    The current user is always assumed to be the owner of the project in this
    view.
    """

    template_name = 'project-admin.html'

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

    def get_project_serialized_data(self):
        project = self.get_template_project()
        if project:
            project.template = project
        serializer = TemplateProjectSerializer(project)
        return serializer.data

    def get_project_is_editable(self):
        return True

    def get_s3_upload_path(self):
        owner_slug = self.kwargs['owner_slug']
        return '/'.join([owner_slug, 'new'])

    def get(self, request, owner_slug):
        self.owner = get_object_or_404(Profile, slug=owner_slug)

        # Check whether this page is for the auth'd user
        if not self.owner.authorizes(request.user):
            return redirect('app-user-profile')

        self.project = None
        return super(NewProjectView, self).get(request, owner_slug)


class RoundupView (AlwaysFresh, AppMixin, TemplateView):
    template_name = 'roundup.html'

    def get_context_data(self, **kwargs):
        context = super(RoundupView, self).get_context_data(**kwargs)

        serializer = RoundupSerializer(self.roundup)
        context['roundup'] = self.roundup
        context['roundup_data'] = serializer.data

        return context

    def get(self, request, owner_slug):
        try:
            self.roundup = Roundup.objects.filter(owner__slug=owner_slug)[0]
        except IndexError:
            return redirect('app-profile', profile_slug=owner_slug)
        return super(RoundupView, self).get(request, owner_slug)


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
about_view = AboutView.as_view()
shareabouts_view = ShareaboutsView.as_view()
shareabouts_auth_success_view = ShareaboutsAuthSuccessView.as_view()
shareabouts_auth_error_view = ShareaboutsAuthErrorView.as_view()
open_source_view = OpenSourceView.as_view()
map_flavors_view = MapFlavorsView.as_view()
project_flavor_view = ProjectFlavorView.as_view()
project_expired_view = ExpiredProjectView.as_view()

project_editor_view = ProjectEditorView.as_view()
project_dashboard_view = ProjectDashboardView.as_view()
project_payments_view = ProjectPaymentsView.as_view()
project_payments_success_view = ProjectPaymentsSuccessView.as_view()
project_activation_success_view = ProjectActivationSuccessView.as_view()
project_page_view = ProjectPageView.as_view()
profile_view = ProfileView.as_view()
new_project_view = NewProjectView.as_view()

roundup_view = RoundupView.as_view()

password_reset_view = PasswordResetView.as_view()
password_change_view = PasswordChangeView.as_view()
password_reset_request_view = PasswordResetRequestView.as_view()
password_reset_instructions_view = PasswordResetInstructionsView.as_view()

signup_view = SignupView.as_view()
signin_view = SigninView.as_view()
password_reset_view = PasswordResetView.as_view()
help_view = HelpView.as_view()
robots_view = TemplateView.as_view(template_name='robots.txt', content_type='text/plain')
sitemap_view = SiteMapView.as_view(content_type='text/xml')
