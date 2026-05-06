import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect("77.37.45.107", port=22, username="root", password="password7@@U", timeout=30)

def run(label, cmd):
    print(f">>> {label}")
    _, stdout, _ = client.exec_command(cmd)
    print(stdout.read().decode('utf-8'))

# Turn on DEBUG in .env
run("Enabling DEBUG on VPS...", "sed -i 's/DEBUG=False/DEBUG=True/g' /var/www/eastwestportal/.env")
run("Restarting Gunicorn...", "systemctl restart gunicorn_ewportal")

client.close()
