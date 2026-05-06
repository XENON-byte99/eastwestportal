import paramiko
import time

HOST = "77.37.45.107"
USER = "root"
PASS = "password7@@U"

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, port=22, username=USER, password=PASS, timeout=30)

def run(label, cmd, timeout=120):
    print(f">>> {label}")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=timeout)
    out = stdout.read().decode().strip()
    err = stderr.read().decode().strip()
    code = stdout.channel.recv_exit_status()
    if out: print(f"    {out[:500]}")
    if err and code != 0: print(f"    ERR: {err[:500]}")
    print(f"    [{'OK' if code == 0 else f'FAILED code={code}'}]\n")
    return out, err, code

print("=== Connected to VPS ===\n")

# Generate SSH key on VPS
run("Generating SSH deploy key...",
    "ssh-keygen -t ed25519 -C 'ewportal-vps-deploy' -f /root/.ssh/ewportal_deploy -N '' -q")

# Read the public key
pub_key, _, _ = run("Reading public key...", "cat /root/.ssh/ewportal_deploy.pub")

print("\n" + "="*60)
print("DEPLOY PUBLIC KEY (add this to GitHub):")
print("="*60)
print(pub_key)
print("="*60 + "\n")

# Configure SSH to use this key for github.com
run("Configuring SSH for GitHub...", """cat > /root/.ssh/config << 'EOF'
Host github.com
    HostName github.com
    User git
    IdentityFile /root/.ssh/ewportal_deploy
    StrictHostKeyChecking no
EOF
chmod 600 /root/.ssh/config""")

client.close()
print("Done. Copy the key above and add it to GitHub as a deploy key.")
