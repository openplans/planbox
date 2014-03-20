from django.db import models
from django.utils.translation import ugettext as _


class BaseDomainMappingMixin (object):
    pass


class DomainMapping (BaseDomainMappingMixin, models.Model):
    domain = models.CharField(_('Custom domain'), max_length=250)
    root_path = models.CharField(max_length=250, help_text=_('The path of the root URL for which this domain is a shortcut.'))


class DefaultDomainMapping (BaseDomainMappingMixin):
    def __init__(self, domain):
        self.domain = domain
        self.root_path = ''