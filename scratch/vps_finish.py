import paramiko
import os

os.environ['PYTHONIOENCODING'] = 'utf-8'

HOST = "77.37.45.107"
USER = "root"
PASS = "password7@@U"
SECRET_KEY = "ewu-portal-prod-x9k2m8p4q1r6v3w5"

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, port=22, username=USER, password=PASS, timeout=30)

def run(label, cmd, timeout=300):
    print(f">>> {label}")
    _, stdout, _ = client.exec_command(cmd, timeout=timeout)
    out = stdout.read().decode('utf-8', errors='replace').strip()
    code = stdout.channel.recv_exit_status()
    result = out[-600:] if len(out) > 600 else out
    if result:
        print(f"    {result}")
    print(f"    [{'OK' if code == 0 else f'FAILED code={code}'}]\n")
    return code

print("=== Connected. Completing remaining setup... ===\n")

BASE = "/var/www/eastwestportal"

# mysqlclient already installed via requirements.txt - skip pip step
run("Verifying venv exists...", f"ls {BASE}/.venv/bin/python 2>&1")
run("Running migrations...", f"cd {BASE} && .venv/bin/python manage.py migrate --noinput 2>&1")
run("Collecting static files...", f"cd {BASE} && .venv/bin/python manage.py collectstatic --noinput -v 0 2>&1 | tail -3")
run("Fixing permissions...", f"mkdir -p {BASE}/media {BASE}/staticfiles && chown -R www-data:www-data {BASE}/media {BASE}/staticfiles && chmod 600 {BASE}/.env")

# Gunicorn service
gunicorn_service = f"""[Unit]
Description=EastWest Portal Gunicorn
After=network.target

[Service]
User=root
Group=root
WorkingDirectory={BASE}
ExecStart={BASE}/.venv/bin/gunicorn --workers 3 --bind unix:/run/gunicorn_ewportal.sock config.wsgi:application
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target"""

run("Writing Gunicorn service...", f"printf '%s' '{gunicorn_service}' > /etc/systemd/system/gunicorn_ewportal.service")
run("Enabling Gunicorn...", "systemctl daemon-reload && systemctl enable gunicorn_ewportal && systemctl restart gunicorn_ewportal")
run("Gunicorn status...", "systemctl is-active gunicorn_ewportal && systemctl status gunicorn_ewportal --no-pager -l 2>&1 | head -10")

# Nginx config
nginx_conf = """server {
    listen 80;
    server_name eee.firebaseit.com srv1617830.hstgr.cloud _;

    location / {
        proxy_pass http://unix:/run/gunicorn_ewportal.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    location /media/  { alias /var/www/eastwestportal/media/; }
    location /static/ { alias /var/www/eastwestportal/staticfiles/; }
    client_max_body_size 20M;
}"""

run("Writing Nginx config...", f"printf '%s' '{nginx_conf}' > /etc/nginx/sites-available/eastwestportal")
run("Enabling Nginx site...", "ln -sf /etc/nginx/sites-available/eastwestportal /etc/nginx/sites-enabled/eastwestportal && rm -f /etc/nginx/sites-enabled/default")
run("Testing Nginx...", "nginx -t 2>&1")
run("Restarting Nginx...", "systemctl restart nginx")

run("Nginx status...", "systemctl is-active nginx")
run("HTTP response test...", "curl -s -o /dev/null -w 'HTTP Status: %{http_code}' http://localhost/")

print("\n" + "="*50)
print("DONE! Site: http://eee.firebaseit.com")
print("="*50)
client.close()
