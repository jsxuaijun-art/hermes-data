# SSH Fallback Methods (When paramiko/sshpass unavailable)

In environments without `paramiko`, `sshpass`, `pexpect`, or `pip`/`sudo` (e.g., minimal WSL or container), use the **SSH_ASKPASS trick** to automate password-based SSH authentication. This is a reliable last-resort method that only requires standard `ssh` and the ability to write a shell script.

## The SSH_ASKPASS Trick

### Step 1: Write a password script

```bash
cat > /tmp/ssh-pass.sh << 'EOF'
#!/bin/bash
echo "your_ssh_password_here"
EOF
chmod +x /tmp/ssh-pass.sh
```

### Step 2: SSH with the trick

```bash
DISPLAY=:0 SSH_ASKPASS=/tmp/ssh-pass.sh SSH_ASKPASS_REQUIRE=force \
  ssh -o StrictHostKeyChecking=no user@host "command"
```

### How it works

SSH normally prompts for a password via `/usr/bin/ssh-askpass` (GUI) or `/dev/tty` (terminal). The `SSH_ASKPASS` env var tells SSH which program to call for the password. `SSH_ASKPASS_REQUIRE=force` forces SSH to use `SSH_ASKPASS` even when a TTY is available. `DISPLAY=:0` prevents the "No DISPLAY" warning.

### Step 3: Install SSH key for persistent passwordless access

Once connected, install the client's public key to avoid re-entering passwords:

```bash
# Copy public key from local machine
cat ~/.ssh/id_rsa.pub

# On the remote server via the SSH_ASKPASS trick:
DISPLAY=:0 SSH_ASKPASS=/tmp/ssh-pass.sh SSH_ASKPASS_REQUIRE=force \
  ssh -o StrictHostKeyChecking=no root@host \
  "mkdir -p ~/.ssh && chmod 700 ~/.ssh && echo '$(cat ~/.ssh/id_rsa.pub)' >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys"
```

After this, `ssh user@host` works without any password prompt.

## Comparison vs Other Methods

| Method | Requirements | Best for |
|--------|-------------|----------|
| `sshpass` | Binary package | Automated scripts, CI/CD |
| `paramiko` | Python package | Programmatic SSH with file transfers |
| `pexpect` | Python package | Interactive SSH automation |
| **SSH_ASKPASS trick** | **Only `ssh` + `chmod`** | **Minimal environments, recovery, fallback** |
| Key-based auth | `ssh-keygen` | Long-term persistent access |

## Why you'd need this

Common scenarios where `sshpass`/`paramiko` aren't available:

- **WSL without sudo** — can't `apt-get install sshpass` or `pip install paramiko`
- **Minimal Docker containers** — only `ssh` client installed
- **Fresh cloud VMs** — haven't installed dev tools yet
- **Restricted environments** — no package manager access

## Cleanup

Remove the password script after use:

```bash
rm -f /tmp/ssh-pass.sh
unset SSH_ASKPASS SSH_ASKPASS_REQUIRE DISPLAY
```

## Warning

The password script stores the password in plain text on disk. Use only as a temporary bootstrap step. Always switch to key-based authentication (Step 3) as soon as possible.
