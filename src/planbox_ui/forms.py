from django import forms
from django.conf import settings
from django.template import Context
from django.template.loader import get_template
from django.utils.translation import ugettext as _

from planbox_data.models import UserAuth, Profile


class UserCreationForm(forms.ModelForm):
    """
    A form that creates a user, with no privileges, from the given username and
    password. Adapted from django.contrib.auth.forms.UserCreationForm; this one
    requires a single password field, and also accepts an email address.
    """
    error_message_templates = {
        'duplicate_email': 'message-duplicate-email-error.html',
        'duplicate_username': 'message-duplicate-username-error.html',
    }
    email = forms.EmailField(label=_("Email"), max_length=254)
    username = forms.RegexField(label=_("Username"), max_length=30,
        regex=r'^[\w.@+-]+$',
        help_text=_("Required. 30 characters or fewer. Letters, digits and "
                      "@/./+/-/_ only."),
        error_messages={
            'invalid': _("This value may contain only letters, numbers and "
                         "@/./+/-/_ characters.")})
    password = forms.CharField(label=_("Password"),
        widget=forms.PasswordInput)
    affiliation = forms.CharField(label=_("Organizational Affiliation"), max_length=256)

    class Meta:
        model = UserAuth
        fields = ("username", "email")

    def clean_email(self):
        # If someone has already signed up with a given email address, they
        # probably just forgot they have an account, or forgot their account
        # credentials.
        email = self.cleaned_data["email"]
        try:
            UserAuth._default_manager.get(email__iexact=email)
        except UserAuth.DoesNotExist:
            return email

        error_template = get_template(self.error_message_templates['duplicate_email'])
        raise forms.ValidationError(
            error_template.render(Context({'email': email, 'settings': settings})),
            code='duplicate_email',
        )

    def clean_username(self):
        # Since User.username is unique, this check is redundant,
        # but it sets a nicer error message than the ORM. See #13147.
        username = self.cleaned_data["username"]
        try:
            Profile.objects.get(slug=username)
        except Profile.DoesNotExist:
            return username

        error_template = get_template(self.error_message_templates['duplicate_username'])
        raise forms.ValidationError(
            error_template.render(Context({'username': username, 'settings': settings})),
            code='duplicate_username',
        )

    def save(self, commit=True):
        auth = super(UserCreationForm, self).save(commit=False)
        auth.set_password(self.cleaned_data["password"])
        if commit:
            auth.save()
            auth.profile.affiliation = self.cleaned_data["affiliation"]
            auth.profile.save()

            # TODO: Send welcome email

        return auth
