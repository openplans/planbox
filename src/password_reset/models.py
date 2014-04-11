import datetime
from django.conf import settings
from django.core.mail import send_mail
from django.db import models
from django.template.loader import render_to_string
from django.utils.encoding import python_2_unicode_compatible
from django.utils.timezone import now
from django.utils.translation import ugettext as _


@python_2_unicode_compatible
class PasswordResetRequest (models.Model):
    DEFAULT_EXPIRATION = datetime.timedelta(hours=1)

    token = models.CharField(max_length=200, verbose_name=_('Reset token'))
    auth = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('User Auth Account'))
    requested_at = models.DateTimeField(default=now)
    expires_at = models.DateTimeField(default=lambda: (now() + PasswordResetRequest.DEFAULT_EXPIRATION))

    def __str__(self):
        return str(self.profile)

    def is_expired(self):
        return self.expires_at <= now()

    def send(self, request):
        context_data = {
            'user': self.auth,
            'reset': self,
            'request': request
        }
        subject = render_to_string('password_reset/password-reset-email-subject.txt', context_data)
        body = render_to_string('password_reset/password-reset-email-body.txt', context_data)

        send_mail(subject, body, settings.EMAIL_ADDRESS, [self.auth.email])
