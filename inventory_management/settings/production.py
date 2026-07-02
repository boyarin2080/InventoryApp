"""
Production Django settings for inventory_management project.

This file contains settings specific to the production environment.
"""

import os
from .base import *

# Override base settings for production
DEBUG = False

# Update ALLOWED_HOSTS from environment variable
ALLOWED_HOSTS = os.getenv(
    'DJANGO_ALLOWED_HOSTS',
    'your-domain.com,www.your-domain.com'
).split(',')

# Enable production security settings
# Already enabled in base.py when DEBUG is False
# But we can be more specific here
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Logging configuration for production
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{levelname}] {asctime} {name} {message}',
            'style': '{',
        },
        'simple': {
            'format': '[{levelname}] {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
            'level': 'INFO',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'django.log'),
            'formatter': 'verbose',
            'level': 'WARNING',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True,
        },
        'django.request': {
            'handlers': ['file'],
            'level': 'WARNING',
            'propagate': False,
        },
        'inventory': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

# Email settings for production (if configured)
if os.getenv('DJANGO_EMAIL_HOST'):
    EMAIL_BACKEND = os.getenv(
        'DJANGO_EMAIL_BACKEND',
        'django.core.mail.backends.smtp.EmailBackend'
    )
    EMAIL_HOST = os.getenv('DJANGO_EMAIL_HOST')
    EMAIL_PORT = int(os.getenv('DJANGO_EMAIL_PORT', '587'))
    EMAIL_USE_TLS = os.getenv('DJANGO_EMAIL_USE_TLS', 'True').lower() == 'true'
    EMAIL_HOST_USER = os.getenv('DJANGO_EMAIL_HOST_USER')
    EMAIL_HOST_PASSWORD = os.getenv('DJANGO_EMAIL_HOST_PASSWORD')
    DEFAULT_FROM_EMAIL = os.getenv('DJANGO_DEFAULT_FROM_EMAIL', 'webmaster@localhost')
