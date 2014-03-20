from django.conf import settings
from django.db import models
from django.utils.translation import ugettext as _

try:
    # Python 2
    from urlparse import urljoin
except ImportError:
    # Python 3
    from urllib.parse import urljoin


class BaseDomainMappingMixin (object):
    def fix_url(self, url, default_root=settings.CANONICAL_ROOT):
        # If the URL doesn't start with a / then it isn't an absolute path and
        # we shouldn't modify it.
        if not url.startswith('/'):
            return url

        # If it starts with two slashes, it's a complete absolute URL without
        # a scheme and we shouldn't modify it.
        if url.startswith('//'):
            return url

        # If the url is based deper than our root URL, then we want to strip
        # off the prefix.
        if url.startswith(self.root_path):
            url = url[len(self.root_path):].lstrip('/')
            return '/' + url

        # Otherwise, it should be considered an external URL and we should use
        # the canonical root to fix it.
        return urljoin(default_root, url)


class DomainMapping (BaseDomainMappingMixin, models.Model):
    domain = models.CharField(_('Custom domain'), max_length=250)
    root_path = models.CharField(max_length=250, help_text=_('The path of the root URL for which this domain is a shortcut.'))


class DefaultDomainMapping (BaseDomainMappingMixin):
    def __init__(self, domain):
        self.domain = domain
        self.root_path = ''