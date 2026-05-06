import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect("77.37.45.107", port=22, username="root", password="password7@@U", timeout=30)

def run(label, cmd):
    print(f">>> {label}")
    _, stdout, _ = client.exec_command(cmd)
    print(stdout.read().decode('utf-8'))

# Append testserver to ALLOWED_HOSTS
run("Updating .env...", "sed -i 's/ALLOWED_HOSTS=/ALLOWED_HOSTS=testserver,/g' /var/www/eastwestportal/.env")
run("Restarting Gunicorn...", "systemctl restart gunicorn_ewportal")

# Run SFTP trace script
_, stdout, stderr = client.exec_command("cd /var/www/eastwestportal && .venv/bin/python scratch_trace.py")
print("=== STDOUT ===")
print(stdout.read().decode('utf-8'))
print("=== STDERR ===")
print(stderr.read().decode('utf-8'))

client.close()
