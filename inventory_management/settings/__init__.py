"""
Django settings package for inventory_management project.

This package loads environment-specific settings based on the
DJANGO_ENVIRONMENT variable.
"""

import os
from .base import *

# Determine the current environment
DJANGO_ENVIRONMENT = os.getenv('DJANGO_ENVIRONMENT', 'development')

# Import environment-specific settings if they exist
if DJANGO_ENVIRONMENT == 'production':
    from .production import *
elif DJANGO_ENVIRONMENT == 'staging':
    from .staging import *
