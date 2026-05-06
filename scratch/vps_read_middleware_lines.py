import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect("77.37.45.107", port=22, username="root", password="password7@@U", timeout=30)

# Print lines 80-95 of config/settings.py on the VPS
_, stdout, _ = client.exec_command("sed -n '80,95p' /var/www/eastwestportal/config/settings.py")
print(stdout.read().decode('utf-8', errors='replace'))

client.close()
