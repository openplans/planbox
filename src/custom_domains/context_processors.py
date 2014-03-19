from __future__ import unicode_literals

from django.conf import settings


class StaticContextProcessor (object):
    """
    Overrides django.core.context_processors.static to take custom domains
    into account
    """
    static_url = None

    def __call__(self, request):
        if self.static_url is None:
            self.static_url = request.build_absolute_uri(settings.STATIC_URL)

        return {'STATIC_URL': self.static_url}

static = StaticContextProcessor()
