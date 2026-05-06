import paramiko

HOST = "77.37.45.107"
USER = "root"
PASS = "password7@@U"
SECRET_KEY = "ewu-portal-prod-x9k2m8p4q1r6v3w5"

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, port=22, username=USER, password=PASS, timeout=30)

def run(label, cmd, timeout=300):
    print(f">>> {label}")
    _, stdout, _ = client.exec_command(cmd, timeout=timeout, get_pty=True)
    out = stdout.read().decode().strip()
    code = stdout.channel.recv_exit_status()
    result = out[-800:] if len(out) > 800 else out
    if result:
        print(f"    {result}")
    print(f"    [{'OK' if code == 0 else f'FAILED code={code}'}]\n")
    return code

print("=== Connected to VPS ===\n")

# Clean slate
run("Cleaning old directory...", "rm -rf /var/www/eastwestportal && mkdir -p /var/www/eastwestportal")

# Clone via SSH deploy key (now authorized on GitHub)
rc = run("Cloning via SSH deploy key...",
    "GIT_SSH_COMMAND='ssh -i /root/.ssh/ewportal_deploy -o StrictHostKeyChecking=no' "
    "git clone git@github.com:XENON-byte99/eastwestportal.git /var/www/eastwestportal 2>&1")

if rc != 0:
    print("!!! Clone still failed. Exiting.")
    client.close()
    exit(1)

run("Setting up virtual environment...", "cd /var/www/eastwestportal && python3 -m venv .venv")
run("Installing requirements...", "cd /var/www/eastwestportal && .venv/bin/pip install -r requirements.txt 2>&1 | tail -5")

run("Writing .env...", f"""cat > /var/www/eastwestportal/.env << 'ENVEOF'
DEBUG=False
SECRET_KEY={SECRET_KEY}
ALLOWED_HOSTS=eee.firebaseit.com,srv1617830.hstgr.cloud,localhost,127.0.0.1
DB_ENGINE=django.db.backends.mysql
DB_NAME=ewportal_db
DB_USER=ewportal_user
DB_PASSWORD=EWPortalDB2024!
DB_HOST=127.0.0.1
DB_PORT=3306
CSRF_TRUSTED_ORIGINS=https://eee.firebaseit.com,http://srv1617830.hstgr.cloud
ENVEOF""")

run("Starting MySQL...", "systemctl start mysql && systemctl enable mysql")
run("Creating DB & user...", """mysql -u root -e "CREATE DATABASE IF NOT EXISTS ewportal_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci; CREATE USER IF NOT EXISTS 'ewportal_user'@'localhost' IDENTIFIED BY 'EWPortalDB2024!'; GRANT ALL PRIVILEGES ON ewportal_db.* TO 'ewportal_user'@'localhost'; FLUSH PRIVILEGES;" 2>&1""")
run("Installing MySQL dev headers...", "apt-get install -y libmysqlclient-dev pkg-config -qq 2>&1 | tail -3")
run("Installing mysqlclient...", "cd /var/www/eastwestportal && .venv/bin/pip install mysqlclient -q 2>&1")

run("Running migrations...", "cd /var/www/eastwestportal && .venv/bin/python manage.py migrate --noinput 2>&1")
run("Collecting static files...", "cd /var/www/eastwestportal && .venv/bin/python manage.py collectstatic --noinput -v 0 2>&1 | tail -3")

run("Fixing permissions...", "mkdir -p /var/www/eastwestportal/media /var/www/eastwestportal/staticfiles && chown -R www-data:www-data /var/www/eastwestportal/media /var/www/eastwestportal/staticfiles && chmod 600 /var/www/eastwestportal/.env")

run("Installing Gunicorn systemd service...", """cat > /etc/systemd/system/gunicorn_ewportal.service << 'SVCEOF'
[Unit]
Description=EastWest Portal Gunicorn
After=network.target

[Service]
User=root
Group=root
WorkingDirectory=/var/www/eastwestportal
ExecStart=/var/www/eastwestportal/.venv/bin/gunicorn --workers 3 --bind unix:/run/gunicorn_ewportal.sock config.wsgi:application
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
SVCEOF
systemctl daemon-reload && systemctl enable gunicorn_ewportal && systemctl restart gunicorn_ewportal""")

run("Installing Nginx config...", """cat > /etc/nginx/sites-available/eastwestportal << 'NGEOF'
server {
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
}
NGEOF""")

run("Enabling Nginx site...", "ln -sf /etc/nginx/sites-available/eastwestportal /etc/nginx/sites-enabled/eastwestportal && rm -f /etc/nginx/sites-enabled/default")
run("Testing Nginx config...", "nginx -t 2>&1")
run("Restarting Nginx...", "systemctl restart nginx")

run("Gunicorn status...", "systemctl is-active gunicorn_ewportal")
run("Nginx status...", "systemctl is-active nginx")
run("HTTP test...", "curl -s -o /dev/null -w 'HTTP Status: %{http_code}' http://localhost/")

# Also configure git to always use the deploy key for future auto-deploys
run("Configuring git for auto-deploy pulls...", """cat >> /root/.bashrc << 'BEOF'
export GIT_SSH_COMMAND="ssh -i /root/.ssh/ewportal_deploy -o StrictHostKeyChecking=no"
BEOF""")

print("\n" + "="*50)
print("DEPLOYMENT COMPLETE!")
print(f"Site: http://eee.firebaseit.com")
print(f"VPS:  http://srv1617830.hstgr.cloud")
print("="*50)
client.close()
