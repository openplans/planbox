"""
WSGI config for planbox project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/howto/deployment/wsgi/
"""

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "planbox.settings")

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

# Send errors to Sentry
# TODO: Move this middleware to the bottom of the module if and when
#       https://github.com/kennethreitz/dj-static/pull/36 gets resolved.
from raven.contrib.django.raven_compat.middleware.wsgi import Sentry
application = Sentry(application)

from dj_static import Cling
application = Cling(application)

from .gzip_middleware import GzipMiddleware
application = GzipMiddleware(application)

from .twinkie import ExpiresMiddleware
application = ExpiresMiddleware(application, {
    'application/javascript': 365*24*60*60,
    'text/css':               365*24*60*60,
    'image/png':              365*24*60*60,
})
