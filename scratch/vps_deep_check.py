import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect("77.37.45.107", port=22, username="root", password="password7@@U", timeout=30)

def run(label, cmd):
    print(f">>> {label}")
    _, stdout, stderr = client.exec_command(cmd)
    out = stdout.read().decode('utf-8')
    err = stderr.read().decode('utf-8')
    if out: print(out)
    if err: print(f"ERROR: {err}")

# Check if the new files exist on the VPS
run("Checking for sw.js...", "ls -l /var/www/eastwestportal/static/js/sw.js")
run("Checking for signals.py...", "ls -l /var/www/eastwestportal/core/signals.py")

# Check if Gunicorn is running the right code (check process start time)
run("Gunicorn process info...", "ps aux | grep gunicorn")

# Force kill and restart
run("Force killing gunicorn...", "pkill -f gunicorn")
run("Restarting gunicorn...", "systemctl restart gunicorn_ewportal")
run("Gunicorn status...", "systemctl status gunicorn_ewportal --no-pager")

client.close()
