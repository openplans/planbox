from __future__ import unicode_literals

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

try:
    # Python 2
    from urlparse import urlparse
except ImportError:
    # Python 3
    from urllib.parse import urlparse


def is_absolute(url):
    result = urlparse(url)
    return result.netloc != ''


class StaticContextProcessor (object):
    """
    Overrides django.core.context_processors.static to take custom domains
    into account
    """
    static_url = None

    def __call__(self, request):
        if self.static_url is None:
            if is_absolute(settings.STATIC_URL):
                self.static_url = settings.STATIC_URL
            else:
                if not hasattr(settings, 'CANONICAL_ROOT'):
                    raise ImproperlyConfigured(
                        'You must provide a CANONICAL_ROOT setting when the '
                        'STATIC_URL is not absolute.')

                self.static_url = '/'.join([
                    settings.CANONICAL_ROOT.rstrip('/'),
                    settings.STATIC_URL.lstrip('/')
                ])

        return {'STATIC_URL': self.static_url}

static = StaticContextProcessor()
