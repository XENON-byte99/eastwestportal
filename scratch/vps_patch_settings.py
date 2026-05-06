import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect("77.37.45.107", port=22, username="root", password="password7@@U", timeout=30)

def run(label, cmd, timeout=300):
    print(f">>> {label}")
    _, stdout, _ = client.exec_command(cmd, timeout=timeout)
    out = stdout.read().decode('utf-8', errors='replace').strip()
    code = stdout.channel.recv_exit_status()
    if out:
        print(f"    {out}")
    print(f"    [{'OK' if code == 0 else f'FAILED code={code}'}]\n")
    return code

print("=== Patching settings.py on VPS ===\n")

# Use sed to add the missing line in settings.py after "if not DEBUG:"
patch_cmd = "sed -i \"/if not DEBUG:/a \\    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')\" /var/www/eastwestportal/config/settings.py"
run("Patching settings.py...", patch_cmd)

run("Restarting Gunicorn...", "systemctl restart gunicorn_ewportal")
run("Verifying status...", "systemctl is-active gunicorn_ewportal")

client.close()
