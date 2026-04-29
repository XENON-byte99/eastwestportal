from django.contrib.auth import get_user_model
User = get_user_model()
users = User.objects.all()
for u in users:
    u.set_password('password123')
    u.save()
    print(f'Updated password for {u.email}')
