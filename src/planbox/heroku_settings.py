import os
import datetime

# Debug is False by default, true if set in the environment.
DEBUG = (os.environ.get('DEBUG', 'False') in ['true', 'True'])
TEMPLATE_DEBUG = DEBUG
SHOW_DEBUG_TOOLBAR = (os.environ.get('SHOW_DEBUG_TOOLBAR', 'False') in ['true', 'True']) or DEBUG
SSL_ENABLED = (os.environ.get('DEBUG', 'True') in ['true', 'True'])

# STATIC_ROOT should be set the same here as in settings.py
STATIC_ROOT = rel_path('../../staticfiles')
STATIC_URL = '/static/'

SECRET_KEY = 'changemeloremipsumdolorsitametconsecteturadipisicingelit'
ALLOWED_HOSTS = ['*']

# Get the list of administrators that get notified on 500 errors
ADMINS = [
    (admin.split('@')[0], admin)
    for admin in os.environ.get('ADMINS', '').split(',')
]

EMAIL_SUBJECT_PREFIX = '[planbox] '

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', 'your_email@example.com')
EMAIL_PORT = os.environ.get('EMAIL_PORT', 587)
EMAIL_USE_TLS = True
SERVER_EMAIL = EMAIL_HOST_USER

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

# GOOGLE_ANALYTICS_ID = os.environ.get('GOOGLE_ANALYTICS_ID', "', ''); alert('Set your Google Analytics ID and domain!'); (function(){})('")
# GOOGLE_ANALYTICS_DOMAIN = os.environ.get('GOOGLE_ANALYTICS_DOMAIN', 'dotcloud.com')

## ===========================================================================

# For sitemaps and caching -- will be a new value every time the server starts
LAST_DEPLOY_DATE = datetime.datetime.now().isoformat()

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
