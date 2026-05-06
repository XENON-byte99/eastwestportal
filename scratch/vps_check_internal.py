import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()
from django.conf import settings
print("MIDDLEWARE:")
for m in settings.MIDDLEWARE:
    print(" -", m)
