import os
import sys
import django
import random
import string

# Setup Django environment
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()

faculty_data = [
    ("Anisul", "Haque", "Professor"),
    ("Khairul", "Alam", "Professor"),
    ("Mohammad Mojammel", "Al Hakim", "Professor"),
    ("Mohammad Ryyan", "Khan", "Associate Professor"),
    ("Mohammed Moseeur", "Rahman", "Associate Professor"),
    ("Ratil", "Hasnat", "Associate Professor"),
    ("Fakir Mashuque", "Alamgir", "Associate Professor"),
    ("Muhammed Mazharul", "Islam", "Assistant Professor"),
    ("Halima", "Begum", "Assistant Professor"),
    ("Farhana", "Parveen", "Assistant Professor"),
    ("Kamanashis", "Saha", "Senior Lecturer"),
    ("Md. Abdur", "Rahman", "Senior Lecturer"),
    ("Shovon", "Talukder", "Senior Lecturer"),
    ("S. M. Raiyan", "Chowdhury", "Lecturer"),
    ("Rizwan", "Shaikh", "Lecturer"),
    ("Sidrat Muntaha Nur", "Pranto", "Lecturer"),
]

def generate_password(length=10):
    characters = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(random.choice(characters) for i in range(length))

print("| Name | Email | Password | Role |")
print("| --- | --- | --- | --- |")

for first_name, last_name, bio in faculty_data:
    # Generate email
    email_prefix = f"{first_name.split()[0].lower()}.{last_name.split()[-1].lower()}"
    email = f"{email_prefix}@ewubd.edu"
    
    # Ensure uniqueness (simple check)
    count = 1
    original_email = email
    while User.objects.filter(email=email).exists():
        email = f"{email_prefix}{count}@ewubd.edu"
        count += 1
    
    username = email
    password = generate_password()
    
    user, created = User.objects.get_or_create(
        email=email,
        defaults={
            'username': username,
            'first_name': first_name,
            'last_name': last_name,
            'role': 'faculty',
            'is_approved': True,
            'department': 'EEE',
            'bio': bio,
            'is_active': True
        }
    )
    
    if created:
        user.set_password(password)
        user.save()
        print(f"| {first_name} {last_name} | {email} | {password} | {bio} |")
    else:
        print(f"| {first_name} {last_name} | {email} | (Already exists) | {bio} |")

print("\nDone adding faculty users.")
