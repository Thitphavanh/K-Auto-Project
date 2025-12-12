"""
Development settings for K-Auto project
"""

from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

# CORS Settings for development
CORS_ALLOW_ALL_ORIGINS = True

# Database - Can use SQLite for quick local development
# Uncomment this to use SQLite instead of PostgreSQL
# DATABASES = {
#     "default": {
#         "ENGINE": "django.db.backends.sqlite3",
#         "NAME": BASE_DIR / "db.sqlite3",
#     }
# }

# Email backend for development (prints to console)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Logging - More verbose in development
LOGGING['root']['level'] = 'DEBUG'
LOGGING['loggers']['django']['level'] = 'DEBUG'

# Cache - Can disable cache in development if needed
# CACHES = {
#     'default': {
#         'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
#     }
# }

# Show SQL queries in console (useful for debugging)
# LOGGING['loggers']['django.db.backends'] = {
#     'handlers': ['console'],
#     'level': 'DEBUG',
# }

print("🚀 Running in DEVELOPMENT mode")
