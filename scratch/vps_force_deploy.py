import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect("77.37.45.107", port=22, username="root", password="password7@@U", timeout=30)

def run(label, cmd):
    print(f">>> {label}")
    _, stdout, _ = client.exec_command(cmd)
    print(stdout.read().decode('utf-8'))

run("Fetching latest origin...", "cd /var/www/eastwestportal && GIT_SSH_COMMAND='ssh -i /root/.ssh/ewportal_deploy -o StrictHostKeyChecking=no' git fetch origin master")
run("Hard reset to FETCH_HEAD...", "cd /var/www/eastwestportal && git reset --hard FETCH_HEAD")
run("Restarting Gunicorn...", "systemctl restart gunicorn_ewportal")

client.close()
