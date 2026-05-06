import paramiko

HOST = "77.37.45.107"
USER = "root"
PASS = "password7@@U"

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, port=22, username=USER, password=PASS, timeout=30)

def run(label, cmd, timeout=300):
    print(f"=== {label} ===")
    _, stdout, stderr = client.exec_command(cmd, timeout=timeout)
    out = stdout.read().decode('utf-8', errors='replace').strip()
    err = stderr.read().decode('utf-8', errors='replace').strip()
    if out:
        print(f"STDOUT:\n{out}")
    if err:
        print(f"STDERR:\n{err}")
    print("\n")

run("Nginx Error Log", "tail -n 20 /var/log/nginx/error.log")
run("Nginx Access Log", "tail -n 20 /var/log/nginx/access.log")
run("Gunicorn Logs", "journalctl -u gunicorn_ewportal -n 30 --no-pager")

client.close()
