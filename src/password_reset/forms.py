import uuid
from django import forms
from django.contrib.auth import get_user_model, authenticate
from django.utils.translation import ugettext as _
from password_reset.models import PasswordResetRequest


class PasswordConfirmationMixin(object):
    def __init__(self, *args, **kwargs):
        super(PasswordConfirmationMixin, self).__init__(*args, **kwargs)
        if not hasattr(self, 'error_messages'):
            self.error_messages = {}
        self.error_messages['password_mismatch'] = _("Your two passwords didn't match.")

    def clean_password_confirm(self, password_field='password', password_confirm_field='password_confirm'):
        password = self.cleaned_data.get(password_field)
        password_confirm = self.cleaned_data.get(password_confirm_field)
        if password and password != password_confirm:
            raise forms.ValidationError(
                self.error_messages['password_mismatch'],
                code='password_mismatch',
            )
        return password_confirm


class PasswordResetRequestForm (forms.Form):
    error_messages = {
        'invalid_email': _("No user with that email address was found. Please check the address and try again."),
    }

    email = forms.EmailField()

    def clean_email(self):
        UserAuth = get_user_model()
        email = self.cleaned_data.get('email')
        try:
            self.user = UserAuth.objects.get(email=email)
        except UserAuth.DoesNotExist:
            raise forms.ValidationError(
                self.error_messages['invalid_email'],
                code='invalid_email',
            )

    def save(self, commit=True):
        reset = PasswordResetRequest(auth=self.user, token=uuid.uuid4())
        if commit:
            reset.save()
        self.reset = reset
        return reset


class SetPasswordForm(PasswordConfirmationMixin, forms.Form):
    """
    A form that lets a user change set his/her password without entering the
    old password
    """
    password = forms.CharField(label=_("New password"), widget=forms.PasswordInput)
    password_confirm = forms.CharField(label=_("Confirm new password"), widget=forms.PasswordInput)

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(SetPasswordForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        username = self.user.username
        password = self.cleaned_data['password']

        self.user.set_password(password)
        if commit:
            self.user.save()
            self.user = authenticate(username=username, password=password)
        return self.user

    def get_user(self):
        return self.user
