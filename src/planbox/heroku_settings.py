import os
import datetime

# Make filepaths relative to settings.
def rel_path(*subs):
    """Make filepaths relative to this settings file"""
    root_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(root_path, *subs)

# Debug is False by default, true if set in the environment.
DEBUG = (os.environ.get('DEBUG', 'False') in ['true', 'True'])
TEMPLATE_DEBUG = DEBUG
SHOW_DEBUG_TOOLBAR = (os.environ.get('SHOW_DEBUG_TOOLBAR', 'False') in ['true', 'True']) or DEBUG

STATIC_ROOT = 'staticfiles'
STATIC_URL = '/static/'
STATICFILES_DIRS = (
    rel_path('../static'),
)

SECRET_KEY = 'changemeloremipsumdolorsitametconsecteturadipisicingelit'
ALLOWED_HOSTS = ['*']

ADMINS = [
    (admin.split('@')[0], admin)
    for admin in os.environ.get('ADMINS', '').split(',')
]

EMAIL_SUBJECT_PREFIX = '[hatch] '

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', 'your_email@example.com')
EMAIL_PORT = os.environ.get('EMAIL_PORT', 587)
EMAIL_USE_TLS = True
SERVER_EMAIL = EMAIL_HOST_USER

import dj_database_url
DATABASES = {'default': dj_database_url.config()}

# import django_cache_url
# CACHES = {'default': django_cache_url.config()}

scheme, connstring = os.environ['CACHE_URL'].split('://')
userpass, fullnetloc = connstring.split('@')
netloc, path = fullnetloc.split('/', 1)
userename, password = userpass.split(':')
CACHES = {
    "default": {
        "BACKEND": "redis_cache.cache.RedisCache",
        "LOCATION": "%s:%s" % (netloc, path),
        "OPTIONS": {
            "CLIENT_CLASS": "redis_cache.client.DefaultClient",
            "PASSWORD": password,
        }
    }
}

SESSION_ENGINE = "django.contrib.sessions.backends.cache"

# Image storing
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto.S3BotoStorage'
AWS_ACCESS_KEY_ID = os.environ['AWS_ACCESS_KEY_ID']
AWS_SECRET_ACCESS_KEY = os.environ['AWS_SECRET_ACCESS_KEY']
AWS_STORAGE_BUCKET_NAME = os.environ['AWS_STORAGE_BUCKET_NAME']
AWS_QUERYSTRING_AUTH = False

# SESSION_ENGINE = "django.contrib.sessions.backends.cache"

GOOGLE_ANALYTICS_ID = os.environ.get('GOOGLE_ANALYTICS_ID', "', ''); alert('Set your Google Analytics ID and domain!'); (function(){})('")
GOOGLE_ANALYTICS_DOMAIN = os.environ.get('GOOGLE_ANALYTICS_DOMAIN', 'dotcloud.com')

## ===========================================================================

# For sitemaps and caching -- will be a new value every time the server starts
LAST_DEPLOY_DATE = datetime.datetime.now().isoformat()

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
            'level': 'DEBUG' if DEBUG else 'INFO',
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
        },
        'hatch': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    }
}
