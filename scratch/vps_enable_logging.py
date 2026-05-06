import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect("77.37.45.107", port=22, username="root", password="password7@@U", timeout=30)

def run(label, cmd):
    print(f">>> {label}")
    _, stdout, _ = client.exec_command(cmd)
    print(stdout.read().decode('utf-8'))

# Update the service file with log flags
service_content = """[Unit]
Description=EastWest Portal Gunicorn
After=network.target

[Service]
User=root
Group=root
WorkingDirectory=/var/www/eastwestportal
ExecStart=/var/www/eastwestportal/.venv/bin/gunicorn --workers 3 --bind unix:/run/gunicorn_ewportal.sock --access-logfile - --error-logfile - config.wsgi:application
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
"""

run("Writing Gunicorn service with logging...", f"printf '%s' '{service_content}' > /etc/systemd/system/gunicorn_ewportal.service")
run("Reloading systemd and restarting...", "systemctl daemon-reload && systemctl restart gunicorn_ewportal")
run("Status...", "systemctl is-active gunicorn_ewportal")

client.close()
