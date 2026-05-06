import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect("77.37.45.107", port=22, username="root", password="password7@@U", timeout=30)

def run(label, cmd):
    print(f"=== {label} ===")
    _, stdout, _ = client.exec_command(cmd)
    print(stdout.read().decode('utf-8'))
    print("\n")

run("Nginx Access Logs", "tail -n 30 /var/log/nginx/access.log")
run("Nginx Error Logs", "tail -n 30 /var/log/nginx/error.log")
run("Gunicorn journal", "journalctl -u gunicorn_ewportal -n 20 --no-pager")

client.close()
