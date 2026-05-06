import paramiko
import os
import time

HOST = "77.37.45.107"
USER = "root"
PASS = "password7@@U"

print("Connecting via SSH...")
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, username=USER, password=PASS)

print("Connecting via SFTP...")
sftp = ssh.open_sftp()
local_zip = "deploy_package.zip"
remote_zip = "/var/www/eastwestportal/deploy_package.zip"

print("Uploading deploy_package.zip... This may take a minute.")
sftp.put(local_zip, remote_zip)
print("Upload complete.")
sftp.close()

commands = [
    "cd /var/www/eastwestportal && GIT_SSH_COMMAND='ssh -i /root/.ssh/ewportal_deploy -o StrictHostKeyChecking=no' git fetch origin master && git reset --hard origin/master",
    "cd /var/www/eastwestportal && apt-get update && apt-get install -y unzip",
    "cd /var/www/eastwestportal && unzip -o deploy_package.zip",
    "cd /var/www/eastwestportal && source .venv/bin/activate && python manage.py migrate --noinput",
    "cd /var/www/eastwestportal && source .venv/bin/activate && python manage.py flush --no-input",
    "cd /var/www/eastwestportal && source .venv/bin/activate && python manage.py loaddata data_dump.json",
    "cd /var/www/eastwestportal && chown -R www-data:www-data media",
    "systemctl restart gunicorn_ewportal"
]

for cmd in commands:
    print(f"Running: {cmd}")
    stdin, stdout, stderr = ssh.exec_command(cmd)
    exit_status = stdout.channel.recv_exit_status()
    out = stdout.read().decode()
    err = stderr.read().decode()
    if out:
        print(out)
    if exit_status != 0:
        print(f"Error ({exit_status}): {err}")
        
ssh.close()
print("Deployment completed successfully.")
