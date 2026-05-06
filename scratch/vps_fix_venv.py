import paramiko, os
os.environ['PYTHONIOENCODING'] = 'utf-8'

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect("77.37.45.107", port=22, username="root", password="password7@@U", timeout=30)

def run(label, cmd, timeout=300):
    print(f">>> {label}")
    _, stdout, _ = client.exec_command(cmd, timeout=timeout)
    out = stdout.read().decode('utf-8', errors='replace').strip()
    code = stdout.channel.recv_exit_status()
    if out: print(f"    {out[-600:]}")
    print(f"    [{'OK' if code == 0 else f'FAILED code={code}'}]\n")
    return code

print("=== Diagnosing VPS state ===\n")

# Check what's in the project dir
run("Listing /var/www/eastwestportal...", "ls -la /var/www/eastwestportal/")
run("Checking venv location...", "find /var/www/eastwestportal -name 'python3' -o -name 'activate' 2>/dev/null | head -5")
run("Checking manage.py...", "ls -la /var/www/eastwestportal/manage.py 2>&1")

# If venv missing, create it
run("Creating venv if missing...", "[ ! -f /var/www/eastwestportal/.venv/bin/python ] && python3 -m venv /var/www/eastwestportal/.venv || echo 'venv already exists'")
run("Installing requirements...", "/var/www/eastwestportal/.venv/bin/pip install -r /var/www/eastwestportal/requirements.txt 2>&1 | tail -5")
run("Running migrations...", "/var/www/eastwestportal/.venv/bin/python /var/www/eastwestportal/manage.py migrate --noinput 2>&1")
run("Collecting static files...", "/var/www/eastwestportal/.venv/bin/python /var/www/eastwestportal/manage.py collectstatic --noinput -v 0 2>&1 | tail -3")

run("Restarting gunicorn...", "systemctl restart gunicorn_ewportal && sleep 2 && systemctl is-active gunicorn_ewportal")
run("HTTP test...", "curl -s -o /dev/null -w 'HTTP: %{http_code}' http://localhost/")

client.close()
