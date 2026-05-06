import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect("77.37.45.107", port=22, username="root", password="password7@@U", timeout=30)

cmd_script = """
import os, django
from django.test import Client

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

c = Client()
try:
    response = c.post('/accounts/login/', {'login': 'testuser@ewubd.edu', 'password': 'testpassword'})
    print("STATUS_CODE:", response.status_code)
    print("CONTENT:", response.content.decode('utf-8'))
except Exception as e:
    import traceback
    print("EXCEPTION_OCCURRED")
    traceback.print_exc()
"""

cmd = f"cd /var/www/eastwestportal && .venv/bin/python -c \"{cmd_script}\""
_, stdout, _ = client.exec_command(cmd)
print(stdout.read().decode('utf-8'))

client.close()
