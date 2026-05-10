import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect("77.37.45.107", port=22, username="root", password="password7@@U", timeout=30)

def run(label, cmd):
    print(f">>> {label}")
    _, stdout, stderr = client.exec_command(cmd)
    out = stdout.read().decode('utf-8')
    err = stderr.read().decode('utf-8')
    if out: print(f"STDOUT: {out}")
    if err: print(f"STDERR: {err}")

# Check current state
run("Checking current directory and remote...", "cd /var/www/eastwestportal && pwd && git remote -v")
run("Checking current branch...", "cd /var/www/eastwestportal && git branch")
run("Checking last 3 commits...", "cd /var/www/eastwestportal && git log -n 3 --oneline")
run("Checking for local changes on VPS...", "cd /var/www/eastwestportal && git status")

client.close()
