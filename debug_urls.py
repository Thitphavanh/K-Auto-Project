import os
import django
from django.urls import URLResolver

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.base")
django.setup()

from config.urls import urlpatterns

print("Checking urlpatterns for missing 'name' attribute...")
for pattern in urlpatterns:
    print(f"Pattern: {pattern}")
    if isinstance(pattern, URLResolver):
        print(f"  Type: URLResolver")
        try:
            print(f"  Name: {pattern.name}")
        except AttributeError:
            print("  Name: MISSING (AttributeError)")
        except Exception as e:
            print(f"  Name: Error ({e})")
    else:
        print(f"  Type: {type(pattern)}")
        print(f"  Name: {getattr(pattern, 'name', 'N/A')}")
