import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect("77.37.45.107", port=22, username="root", password="password7@@U", timeout=30)

cmd = "grep 'CsrfViewMiddleware' /var/www/eastwestportal/config/settings.py"
_, stdout, _ = client.exec_command(cmd)
print(stdout.read().decode('utf-8', errors='replace'))

client.close()
