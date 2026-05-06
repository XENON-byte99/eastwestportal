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
    if out: print(f"    {out[-1000:]}")
    print(f"    [{'OK' if code == 0 else f'FAILED code={code}'}]\n")
    return code

# Check if clone ended up in a subdirectory
run("Checking if project in subdirectory...", "find /var/www -name 'manage.py' 2>/dev/null")
run("Check .venv contents...", "ls /var/www/eastwestportal/.venv/bin/ | head -10")

# Re-clone cleanly - only delete project files, keep .venv
run("Removing old project files only...", "find /var/www/eastwestportal -mindepth 1 -maxdepth 1 ! -name '.venv' ! -name '.env' ! -name 'media' ! -name 'staticfiles' -delete")

# Re-clone
run("Re-cloning repository...",
    "GIT_SSH_COMMAND='ssh -i /root/.ssh/ewportal_deploy -o StrictHostKeyChecking=no' "
    "git clone git@github.com:XENON-byte99/eastwestportal.git /tmp/ewportal_tmp 2>&1 && "
    "cp -r /tmp/ewportal_tmp/. /var/www/eastwestportal/ && "
    "rm -rf /tmp/ewportal_tmp")

run("Verifying clone...", "ls /var/www/eastwestportal/ | head -20")
run("Check manage.py...", "ls -la /var/www/eastwestportal/manage.py")

# Now run setup
run("Installing requirements (using existing venv)...", "/var/www/eastwestportal/.venv/bin/pip install -r /var/www/eastwestportal/requirements.txt 2>&1 | tail -5")
run("Running migrations...", "/var/www/eastwestportal/.venv/bin/python /var/www/eastwestportal/manage.py migrate --noinput 2>&1")
run("Collecting static files...", "/var/www/eastwestportal/.venv/bin/python /var/www/eastwestportal/manage.py collectstatic --noinput -v 0 2>&1 | tail -3")

run("Restarting gunicorn...", "systemctl restart gunicorn_ewportal && sleep 3 && systemctl is-active gunicorn_ewportal")
run("HTTP test...", "curl -s -o /dev/null -w 'HTTP: %{http_code}' http://localhost/")
run("Gunicorn socket...", "ls -la /run/gunicorn_ewportal.sock 2>&1")

print("\n=== DONE ===")
client.close()
