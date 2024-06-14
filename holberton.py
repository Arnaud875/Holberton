import subprocess
import paramiko
import json
import argparse

GITHUB_TOKEN = ""
GITHUB_USERNAME = ""
GITHUB_EMAIL = ""

def local_cache(ssh_port, ssh_host, ssh_pass, git_name):
    print("[*] Saving local cache...")
    with open("local_cache.txt", "w") as f:
        f.write(json.dumps({ "cache": [ssh_port, ssh_host, ssh_pass, git_name] }))

# TODO: Fix error first cloning
def check(err):
    err_stdout = err[2].readline().strip()
    if err_stdout != "":
        if "already exists" in err_stdout:
            return

        print(f"[-] Error command: {err_stdout}")
        exit(-1)

parse = argparse.ArgumentParser()
parse.add_argument("-l", "-local-cache", action="store_true", help="Use local cache")
args = parse.parse_args()

if args.l == True:
    try:
        with open("local_cache.txt", "r") as f:
            data = json.load(f)
            ssh_port = data["cache"][0]
            ssh_host = data["cache"][1]
            ssh_pass = data["cache"][2]
            git_name = data["cache"][3]
    except FileNotFoundError:
        print("[-] Local cache not found.")
        exit(-1)
else:
    ssh_port = input("ssh port: ")
    ssh_host = input("ssh (ex: name@ip): ")
    ssh_pass = input("ssh password: ")
    git_name = input("Git repo: ")

    local_cache(int(ssh_port), ssh_host, ssh_pass, git_name)

username = ssh_host.split("@")[0]
hostname = ssh_host.split("@")[1]

print("[*] Init ssh client...")
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

print("[*] Connecting...")
client.connect(hostname, ssh_port, username, ssh_pass)

print("[*] Init github account...")
check(client.exec_command(f"git config --global user.name {GITHUB_USERNAME}"))
check(client.exec_command(f"git config --global user.email {GITHUB_EMAIL}"))

print(f"[*] Cloning {git_name}...")
check(client.exec_command(f"git clone https://{GITHUB_TOKEN}@github.com/{GITHUB_USERNAME}/{git_name}"))

print("[*] Closing ssh client...")
client.close()

# waring blocked:
# The authenticity of host '[ssh.cod-us-east-1.hbtn.io]:13249 ([34.204.167.66]:13249)' can't be established.
# ED25519 key fingerprint is SHA256:q2+oiY5mFtKvRwYR0uXZFCXNJN8s4HPMwo3eOm4iiHk.
# This host key is known by the following other names/addresses:
#     ~/.ssh/known_hosts:8: [hashed name]
#     ~/.ssh/known_hosts:12: [hashed name]
# Are you sure you want to continue connecting (yes/no/[fingerprint])? yes

# - fix le problème juste au dessus
# - ajouter un système pour vérifier si le projet est déjà clone ou non
# - utiliser pickle pour le système de cache
# - ajouter automatique le fichier push.sh

print("[*] Opening new terminal and connecting ssh...")
subprocess.run(["xfce4-terminal", "--hold", "--command", f"bash -c \"sshpass -p {ssh_pass} ssh -o 'StrictHostKeyChecking no' -p {int(ssh_port)} {username}@{hostname}; exec bash\""])