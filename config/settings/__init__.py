"""
Settings __init__.py
Automatically loads the appropriate settings based on DJANGO_SETTINGS_MODULE environment variable
"""

import os

# Get environment from environment variable, default to 'dev'
environment = os.environ.get('DJANGO_ENV', 'dev')

if environment == 'prod' or environment == 'production':
    from .prod import *
    print("✅ Loaded PRODUCTION settings")
elif environment == 'dev' or environment == 'development':
    from .dev import *
    print("✅ Loaded DEVELOPMENT settings")
else:
    # Default to development
    from .dev import *
    print("✅ Loaded DEVELOPMENT settings (default)")
