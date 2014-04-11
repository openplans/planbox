from django.conf import settings
from django.contrib import messages
from django.contrib import auth
from django.core.urlresolvers import reverse
from django.http import Http404
from django.shortcuts import resolve_url, get_object_or_404
from django.utils.timezone import now
from django.utils.translation import ugettext as _
from django.views.generic import FormView, UpdateView, TemplateView
from password_reset.forms import PasswordResetRequestForm, SetPasswordForm
from password_reset.models import PasswordResetRequest


UserAuth = auth.get_user_model()


class PasswordResetRequestView (FormView):
    form_class = PasswordResetRequestForm
    template_name = 'password_reset/password-reset-request.html'

    def get_success_url(self):
        return reverse('password-reset-instructions')

    def form_valid(self, form):
        response = super(PasswordResetRequestView, self).form_valid(form)
        reset = form.save()
        reset.send(self.request)
        return response


class PasswordResetInstructionsView (TemplateView):
    template_name = 'password_reset/password-reset-request-complete.html'


class BasePasswordChangeView (UpdateView):
    model = UserAuth
    template_name = 'password_reset/password-reset.html'
    form_class = SetPasswordForm

    def get_context_data(self, **kwargs):
        return super(BasePasswordChangeView, self).get_context_data(save_label="Save Password", **kwargs)

    def get_success_url(self):
        return resolve_url(settings.LOGIN_REDIRECT_URL)

    def form_valid(self, form):
        response = super(BasePasswordChangeView, self).form_valid(form)
        user = form.get_user()

        # Log the user in, and give them an appropriate message
        auth.login(self.request, user)
        messages.success(self.request, _('You have successfully changed your password.'))

        return response

    def get_form(self, form_class):
        kwargs = self.get_form_kwargs()
        user = kwargs.pop('instance')
        return form_class(user, **kwargs)


class PasswordChangeView (BasePasswordChangeView):
    def get_object(self, queryset=None):
        user = self.request.user
        if user.is_authenticated():
            return user
        else:
            raise Http404


class PasswordResetView (BasePasswordChangeView):
    def get_object(self, queryset=None):
        token = self.kwargs.get('token')
        self.reset = get_object_or_404(PasswordResetRequest, token=token, expires_at__gt=now())
        return self.reset.auth

    def form_valid(self, form):
        response = super(PasswordResetView, self).form_valid(form)

        # Expire the reset token, since it has been used
        self.reset.expires_at = now()
        self.reset.save()

        return response


password_change_view = PasswordChangeView.as_view()
password_reset_view = PasswordResetView.as_view()
password_reset_request_view = PasswordResetRequestView.as_view()
password_reset_instructions_view = PasswordResetInstructionsView.as_view()