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
    _, stdout, _ = client.exec_command(cmd, timeout=timeout)
    out = stdout.read().decode('utf-8', errors='replace').strip()
    code = stdout.channel.recv_exit_status()
    if out:
        print(f"    {out}")
    print(f"    [{'OK' if code == 0 else f'FAILED code={code}'}]\n")
    return code

# Rewrite .env with HTTP as well as HTTPS for CSRF
run("Writing new .env with HTTP CSRF origins...", f"""cat > /var/www/eastwestportal/.env << 'ENVEOF'
DEBUG=False
SECRET_KEY={SECRET_KEY}
ALLOWED_HOSTS=eee.firebaseit.com,srv1617830.hstgr.cloud,localhost,127.0.0.1
DB_ENGINE=django.db.backends.mysql
DB_NAME=ewportal_db
DB_USER=ewportal_user
DB_PASSWORD=EWPortalDB2024!
DB_HOST=127.0.0.1
DB_PORT=3306
CSRF_TRUSTED_ORIGINS=https://eee.firebaseit.com,http://eee.firebaseit.com,http://srv1617830.hstgr.cloud
ENVEOF""")

run("Restarting Gunicorn...", "systemctl restart gunicorn_ewportal")
run("Gunicorn status...", "systemctl is-active gunicorn_ewportal")

client.close()
