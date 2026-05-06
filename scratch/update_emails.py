import os
import sys
import django

# Setup Django environment
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()

users = User.objects.filter(email__endswith='@ewubd.edu')
for u in users:
    old_email = u.email
    new_email = old_email.replace('@ewubd.edu', '@std.ewubd.edu')
    u.email = new_email
    u.username = new_email
    u.save()
    print(f"Updated {old_email} -> {new_email}")

print("Done updating email extensions.")
