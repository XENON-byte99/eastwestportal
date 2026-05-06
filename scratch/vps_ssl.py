import paramiko

HOST = "77.37.45.107"
USER = "root"
PASS = "password7@@U"

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, port=22, username=USER, password=PASS, timeout=30)

def run(label, cmd, timeout=300):
    print(f">>> {label}")
    _, stdout, stderr = client.exec_command(cmd, timeout=timeout)
    out = stdout.read().decode('utf-8', errors='replace').strip()
    err = stderr.read().decode('utf-8', errors='replace').strip()
    code = stdout.channel.recv_exit_status()
    if out:
        print(f"    OUT: {out}")
    if err and code != 0:
        print(f"    ERR: {err}")
    print(f"    [{'OK' if code == 0 else f'FAILED code={code}'}]\n")
    return code

print("=== Setting up HTTPS with Certbot ===\n")

run("Installing Certbot...", "DEBIAN_FRONTEND=noninteractive apt-get install -y certbot python3-certbot-nginx")
run("Obtaining SSL certificate and configuring Nginx...", "certbot --nginx -d eee.firebaseit.com --non-interactive --agree-tos -m knownas.nahian@gmail.com")
run("Testing Nginx config...", "nginx -t")
run("Restarting Nginx...", "systemctl restart nginx")

client.close()
