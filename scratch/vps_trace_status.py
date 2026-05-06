import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect("77.37.45.107", port=22, username="root", password="password7@@U", timeout=30)

# Create script file locally
local_path = "e:/eastwestportal/scratch/vps_trace_internal_status.py"
with open(local_path, "w", encoding="utf-8") as f:
    f.write("""import os, django
from django.test import Client

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

c = Client()
try:
    print("Executing request...")
    response = c.post('/accounts/login/', {'login': 'testuser@ewubd.edu', 'password': 'testpassword'})
    print("STATUS_CODE:", response.status_code)
    print("Is login successful? (Redirect):", response.get('Location', 'No redirect'))
except Exception as e:
    import traceback
    print("EXCEPTION_OCCURRED")
    traceback.print_exc()
""")

# Upload to VPS via SFTP
sftp = client.open_sftp()
sftp.put(local_path, "/var/www/eastwestportal/scratch_trace.py")
sftp.close()

# Run it
_, stdout, stderr = client.exec_command("cd /var/www/eastwestportal && .venv/bin/python scratch_trace.py")
print("=== STDOUT ===")
print(stdout.read().decode('utf-8'))
print("=== STDERR ===")
print(stderr.read().decode('utf-8'))

client.close()
