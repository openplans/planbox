"""
ssl_required decorator
----------------------
Redirect requests to the given to to HTTPS if they are not secure already.
Source: https://djangosnippets.org/snippets/1351/
Author: pjs (https://djangosnippets.org/users/pjs/)
"""

import urlparse
from django.conf import settings
from django.http import HttpResponsePermanentRedirect


def ssl_required(view_func):
    def _checkssl(request, *args, **kwargs):
        if not settings.DEBUG and not request.is_secure():
            if hasattr(settings, 'SSL_DOMAIN'):
                url_str = urlparse.urljoin(
                    settings.SSL_DOMAIN,
                    request.get_full_path()
                )
            else:
                url_str = request.build_absolute_uri()
            url_str = url_str.replace('http://', 'https://', 1)
            return HttpResponsePermanentRedirect(url_str)

        return view_func(request, *args, **kwargs)
    return _checkssl
