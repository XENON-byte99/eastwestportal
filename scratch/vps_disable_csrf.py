import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect("77.37.45.107", port=22, username="root", password="password7@@U", timeout=30)

def run(label, cmd):
    print(f">>> {label}")
    _, stdout, _ = client.exec_command(cmd)
    print(stdout.read().decode('utf-8'))

# Comment out the CsrfViewMiddleware in settings.py on the VPS
run("Commenting out CsrfViewMiddleware...", "sed -i \"s/'django.middleware.csrf.CsrfViewMiddleware',/# 'django.middleware.csrf.CsrfViewMiddleware',/g\" /var/www/eastwestportal/config/settings.py")
run("Restarting Gunicorn...", "systemctl restart gunicorn_ewportal")
run("Gunicorn status...", "systemctl is-active gunicorn_ewportal")

client.close()
