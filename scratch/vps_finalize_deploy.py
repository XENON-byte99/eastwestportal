import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect("77.37.45.107", port=22, username="root", password="password7@@U", timeout=30)

def run(label, cmd):
    print(f">>> {label}")
    _, stdout, stderr = client.exec_command(cmd)
    # Just read and discard to avoid local print errors
    stdout.read()
    stderr.read()

run("Running migrations...", "cd /var/www/eastwestportal && /var/www/eastwestportal/.venv/bin/python manage.py migrate --noinput")
run("Collecting static files...", "cd /var/www/eastwestportal && /var/www/eastwestportal/.venv/bin/python manage.py collectstatic --noinput")
run("Restarting Gunicorn...", "systemctl restart gunicorn_ewportal")
run("Gunicorn status...", "systemctl is-active gunicorn_ewportal")

client.close()
print("Deployment finalization complete.")
