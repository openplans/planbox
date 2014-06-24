import os
import datetime

# Debug is False by default, true if set in the environment.
DEBUG = (os.environ.get('DEBUG', 'False') in ['true', 'True'])
TEMPLATE_DEBUG = DEBUG
SHOW_DEBUG_TOOLBAR = (os.environ.get('SHOW_DEBUG_TOOLBAR', 'False') in ['true', 'True']) or DEBUG
HTTPS_ENABLED = (os.environ.get('HTTPS', 'on').lower() in ['true', 'on'])
SESSION_COOKIE_SECURE = HTTPS_ENABLED
CSRF_COOKIE_SECURE = HTTPS_ENABLED

# STATIC_ROOT should be set the same here as in settings.py
STATIC_ROOT = rel_path('../../staticfiles')
STATIC_URL = '/static/'

SECRET_KEY = 'changemeloremipsumdolorsitametconsecteturadipisicingelit'
ALLOWED_HOSTS = ['*']
KNOWN_HOSTS = os.environ.get('KNOWN_HOSTS').split(',')

# Get the list of administrators that get notified on 500 errors
ADMINS = [
    (admin.split('@')[0], admin)
    for admin in os.environ.get('ADMINS', '').split(',')
]

EMAIL_SUBJECT_PREFIX = '[planbox] '

# Emailing
if any(email_setting in os.environ
       for email_setting in ['EMAIL_HOST', 'EMAIL_HOST_PASSWORD',
                             'EMAIL_HOST_USER', 'EMAIL_PORT', 'EMAIL_USE_TLS']):
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = os.environ.get('EMAIL_HOST', 'localhost')
    EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
    EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
    EMAIL_PORT = int(os.environ.get('EMAIL_PORT', '25'))
    EMAIL_USE_TLS = (os.environ.get('EMAIL_USE_TLS', 'True').lower() == 'true')
    SERVER_EMAIL = EMAIL_HOST_USER

PLANBOX_CONTACT_EMAIL = os.environ.get('CONTACT_EMAIL', '')
EMAIL_ADDRESS = PLANBOX_CONTACT_EMAIL

import dj_database_url
DATABASES = {'default': dj_database_url.config()}

import django_cache_url
CACHES = {'default': django_cache_url.config()}

# scheme, connstring = os.environ['CACHE_URL'].split('://')
# userpass, fullnetloc = connstring.split('@')
# netloc, path = fullnetloc.split('/', 1)
# userename, password = userpass.split(':')
# CACHES = {
#     "default": {
#         "BACKEND": "redis_cache.cache.RedisCache",
#         "LOCATION": "%s:%s" % (netloc, path),
#         "OPTIONS": {
#             "CLIENT_CLASS": "redis_cache.client.DefaultClient",
#             "PASSWORD": password,
#         }
#     }
# }

# SESSION_ENGINE = "django.contrib.sessions.backends.cache"

GOOGLE_ANALYTICS_ID = os.environ.get('GOOGLE_ANALYTICS_ID', "', ''); alert('Set your Google Analytics ID and domain!'); (function(){})('")
GOOGLE_ANALYTICS_DOMAIN = os.environ.get('GOOGLE_ANALYTICS_DOMAIN', 'herokuapp.com')

# intercom.io
INTERCOM_ID = os.environ.get('INTERCOM_ID', '')
INTERCOM_SECRET = os.environ.get('INTERCOM_SECRET', '')

## ===========================================================================

# For sitemaps and caching -- will be a new value every time the server starts
LAST_DEPLOY_DATE = datetime.datetime.now().replace(second=0, microsecond=0).isoformat()

# S3 stuff
S3_MEDIA_BUCKET = os.environ.get('S3_MEDIA_BUCKET')
AWS_ACCESS_KEY = os.environ.get('AWS_ACCESS_KEY')
AWS_SECRET_KEY = os.environ.get('AWS_SECRET_KEY')

# Shareabouts integration
SHAREABOUTS_HOST = os.environ.get('SHAREABOUTS_HOST')
SHAREABOUTS_USERNAME = os.environ.get('SHAREABOUTS_USERNAME')
SHAREABOUTS_PASSWORD = os.environ.get('SHAREABOUTS_PASSWORD')

LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'formatters': {
        'simple': {
            'format': '%(levelname)s %(asctime)s\n%(message)s',
        },
    },
    'handlers': {
        'console': {
            'level': LOG_LEVEL,
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        'django': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'planbox': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'planbox_data': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'planbox_ui': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
    }
}

