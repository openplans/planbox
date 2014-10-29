from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext as _


@python_2_unicode_compatible
class Preauthorization (models.Model):
    username = models.TextField(blank=True, help_text=_('The username of the Shareabouts user'))
    project = models.OneToOneField('planbox_data.Project', related_name='shareabouts_preauthorization')

    def __str__(self):
        return self.username
