import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect("77.37.45.107", port=22, username="root", password="password7@@U", timeout=30)

cmd = "curl -v -X POST -H 'Host: eee.firebaseit.com' -d 'login=testuser@ewubd.edu&password=testpassword' --unix-socket /run/gunicorn_ewportal.sock http://localhost/accounts/login/"
_, stdout, stderr = client.exec_command(cmd)
print("=== STDOUT ===")
print(stdout.read().decode('utf-8'))
print("=== STDERR ===")
print(stderr.read().decode('utf-8'))

client.close()
