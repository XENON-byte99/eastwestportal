import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect("77.37.45.107", port=22, username="root", password="password7@@U", timeout=30)

def run(label, cmd):
    print(f">>> {label}")
    _, stdout, _ = client.exec_command(cmd)
    print(stdout.read().decode('utf-8'))

# Pull the updates
run("Pulling from master branch...", "cd /var/www/eastwestportal && GIT_SSH_COMMAND='ssh -i /root/.ssh/ewportal_deploy -o StrictHostKeyChecking=no' git pull origin master")

# Reset DEBUG=False
run("Restoring DEBUG=False on VPS...", "sed -i 's/DEBUG=True/DEBUG=False/g' /var/www/eastwestportal/.env")

# Remove testserver from ALLOWED_HOSTS
run("Cleaning ALLOWED_HOSTS on VPS...", "sed -i 's/ALLOWED_HOSTS=testserver,/ALLOWED_HOSTS=/g' /var/www/eastwestportal/.env")

run("Restarting Gunicorn...", "systemctl restart gunicorn_ewportal")
run("Gunicorn status...", "systemctl is-active gunicorn_ewportal")

client.close()
