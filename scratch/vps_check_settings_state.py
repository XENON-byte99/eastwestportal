import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect("77.37.45.107", port=22, username="root", password="password7@@U", timeout=30)

local_path = "e:/eastwestportal/scratch/vps_check_internal.py"
with open(local_path, "w", encoding="utf-8") as f:
    f.write("""import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()
from django.conf import settings
print("MIDDLEWARE:")
for m in settings.MIDDLEWARE:
    print(" -", m)
""")

sftp = client.open_sftp()
sftp.put(local_path, "/var/www/eastwestportal/vps_check_internal.py")
sftp.close()

_, stdout, _ = client.exec_command("cd /var/www/eastwestportal && .venv/bin/python vps_check_internal.py")
print(stdout.read().decode('utf-8'))

client.close()
