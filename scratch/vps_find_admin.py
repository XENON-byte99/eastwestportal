import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect("77.37.45.107", port=22, username="root", password="password7@@U", timeout=30)

cmd = "cd /var/www/eastwestportal && .venv/bin/python -c \"import os, django; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings'); django.setup(); from django.contrib.auth import get_user_model; User = get_user_model(); print([(u.email, u.username) for u in User.objects.filter(is_superuser=True)])\""
_, stdout, _ = client.exec_command(cmd)
print(stdout.read().decode('utf-8'))

client.close()
