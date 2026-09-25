# 阿里云 Cron Job 部署指南

Template + loader cron jobs 部署到阿里云服务器（或任何远程 SSH 服务器）的完整流程。

## 前置条件

- SSH key-based auth to Alibaba Cloud root@47.103.27.171 (see [SSH Key Setup](#ssh-key-setup) below if keys not configured)
- Hermes Gateway running on the remote server

## Step-by-Step Deployment

### Step 1: Prepare Files Locally

```
~/.hermes/cron/
├── my_loader.py        # Python loader script
├── daily_template.md   # Daily prompt template
└── weekly_template.md  # Weekly prompt template (loaded conditionally)
```

### Step 2: SCP to Remote Server

```bash
scp ~/.hermes/cron/*.py root@<ip>:~/.hermes/cron/
scp ~/.hermes/cron/*.md root@<ip>:~/.hermes/cron/
```

Or in one command:
```bash
scp ~/.hermes/cron/{*.py,*.md} root@<ip>:~/.hermes/cron/
```

### Step 3: Create Output Directories

```bash
ssh root@<ip> 'mkdir -p ~/reports/daily ~/reports/weekly'
```

### Step 4: Create Cron Job via `jobs.json`

On Hermes versions where `hermes cron create` has bugs (`KeyError: 2`), write the job directly:

```bash
# Generate unique job ID
JOB_ID=$(python3 -c "import uuid; print(uuid.uuid4().hex[:12])")

# Write jobs.json via SSH
ssh root@<ip> "python3 << 'PYEOF'
import json, os
job = {
    'id': '$JOB_ID',
    'name': 'Unified Cron Job',
    'schedule': '5 9 * * 1,3,5',
    'prompt': 'Execute the instructions in the template output by the loader script.',
    'script': 'cron/my_loader.py',
    'workdir': '/root',
    'deliver': 'local',
    'repeat': 0,
    'enabled_toolsets': ['web', 'terminal', 'file'],
    'no_agent': False
}
config = {'jobs': [job]}
os.makedirs(os.path.expanduser('~/.hermes/cron'), exist_ok=True)
with open(os.path.expanduser('~/.hermes/cron/jobs.json'), 'w') as f:
    json.dump(config, f, indent=2)
print('jobs.json written')
PYEOF"
```

### Step 5: Restart Gateway

```bash
ssh root@<ip> 'hermes gateway restart'
sleep 5
ssh root@<ip> 'hermes cron list'
```

### Step 6: Verify via Manual Trigger

```bash
# 1. Trigger (async — schedules on next tick)
ssh root@<ip> 'cd /root && hermes cron run <job_id>'

# 2. Wait for the scheduler tick  
sleep 45

# 3. Check status
ssh root@<ip> 'hermes cron list'
# Look for: Last run: ... ok

# 4. Verify output files
ssh root@<ip> 'ls -la ~/reports/daily/ && head -10 ~/reports/daily/2026-06-01.md'

# 5. Check gateway logs
ssh root@<ip> 'journalctl -u hermes-gateway --since "3 minutes ago" | tail -20'
```

**Important**: `hermes cron run` returns immediately. Wait ~45 seconds and check status.

### Step 7: Git Backup

```bash
# Copy cron files
cp ~/.hermes/cron/*.py ~/hermes-data/cron/
cp ~/.hermes/cron/*.md ~/hermes-data/cron/

# Also push_report.py and sample outputs
cp /opt/wecom-bot/push_report.py ~/hermes-data/cron/
cp ~/tax_intel/daily/2026-05-31.md ~/hermes-data/examples/

cd ~/hermes-data && git add -A && git commit -m "sync cron files" && git push
```

### Pitfall: `.gitignore` Whitelist Blocks New Directories

If the repo uses `*` in `.gitignore` (exclude-everything-by-default) with whitelists:

```gitignore
# Exclude everything by default
*
!.gitignore
!cron/
!cron/**
```

New directories (e.g., `examples/`) are silently ignored. Fix: add `!examples/` or place files inside already-whitelisted dirs like `cron/`.

## SSH Key Setup (Without sshpass)

When `sshpass`, `expect`, `paramiko` are all unavailable, use SSH_ASKPASS:

```bash
# 1. Generate SSH key
ssh-keygen -t rsa -f ~/.ssh/id_rsa -N "" -q

# 2. Create password script
cat > /tmp/ssh-pass.sh << 'EOF'
#!/bin/bash
echo "<password>"
EOF
chmod +x /tmp/ssh-pass.sh

# 3. Copy public key
DISPLAY=:0 SSH_ASKPASS=/tmp/ssh-pass.sh SSH_ASKPASS_REQUIRE=force \
  ssh -o StrictHostKeyChecking=no root@<ip> \
  "mkdir -p ~/.ssh && chmod 700 ~/.ssh && echo '$(cat ~/.ssh/id_rsa.pub)' >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys"

# 4. Cleanup
rm /tmp/ssh-pass.sh

# 5. Verify
ssh root@<ip> "echo 'OK'"
```

## Writing `.env` Files via SSH (Avoid Shell Expansion)

**NEVER use `sed`** to update `.env` values containing `$`, `.`, `/`, or backticks. `sed` treats `.` as regex wildcard and `$` as line end — silently corrupts API keys.

### Safe: Use base64

```bash
python3 << 'PYEOF'
import subprocess, base64
api_key = "sk-..."
content = f"ANYSEARCH_API_KEY={api_key}\n"
b64 = base64.b64encode(content.encode()).decode()
cmd = f"echo {b64} | base64 -d > /root/.hermes/skills/X/.env"
subprocess.run(['ssh', 'root@<ip>', cmd])
PYEOF
```

### Safe: Write via Python on Remote

```bash
ssh root@<ip> "python3 << 'PYEOF'
api_key = 'sk-...'
lines = open('/root/.hermes/.env', 'r').readlines()
with open('/root/.hermes/.env', 'w') as f:
    for line in lines:
        if line.startswith('DEEPSEEK_API_KEY='):
            f.write(f'DEEPSEEK_API_KEY={api_key}\n')
        else:
            f.write(line)
PYEOF"
```

### Verify

```bash
ssh root@<ip> 'wc -c /root/.hermes/.env'
# Expected: ANYSEARCH_API_KEY (37 chars key) = 57 bytes
# Verify last 4 chars match expected
```

## Extracting Skill Zip Archives

Use Python stdlib (no unzip required):

```python
import urllib.request, zipfile, io, os, shutil
resp = urllib.request.urlopen('https://github.com/<owner>/<repo>/archive/refs/heads/main.zip')
z = zipfile.ZipFile(io.BytesIO(resp.read()))
skill_dir = os.path.expanduser('~/.hermes/skills/<name>/')
if os.path.exists(skill_dir): shutil.rmtree(skill_dir)
os.makedirs(skill_dir)
for f in z.namelist():
    parts = f.split('/', 1)
    if len(parts) > 1:
        target = os.path.join(skill_dir, parts[1])
        if f.endswith('/'): os.makedirs(target, exist_ok=True)
        else:
            os.makedirs(os.path.dirname(target), exist_ok=True)
            with open(target, 'wb') as out: out.write(z.read(f))
```

Works on WSL, Windows Desktop, and Aliyun — anywhere Python 3 is installed.

## Gateway Status & Management

### Check Gateway
```bash
hermes gateway status
# or via systemd: systemctl status hermes-gateway.service
```

### Start/Stop/Restart
```bash
hermes gateway run       # foreground debugging
hermes gateway start     # systemd background
hermes gateway restart   # restart service
hermes gateway stop      # stop service
hermes gateway install   # enable on boot
```

### Alibaba Cloud Recommended Architecture

| Role | Environment | Gateway | Purpose |
|------|-------------|---------|---------|
| **Daily dev** | Local WSL / Windows Desktop | **Stopped** | Interactive coding, debugging |
| **7×24 services** | Alibaba Cloud | **Running** | WeCom bot, cron jobs |

### Keep Local Gateway Stopped
```bash
# Avoid two gateways competing for WeCom connections
hermes gateway stop
systemctl disable hermes-gateway  # prevent auto-start
```

## Git Merge Conflict Fix in Hermes Agent

Hermes agent directory (`~/.hermes/hermes-agent/`) can accumulate merge conflict artifacts after failed git operations:

### Symptoms
```
File "setup.py", line 3297
    <<<<<<< Updated upstream
SyntaxError: invalid syntax
```

### Fix
```bash
cd ~/.hermes/hermes-agent
grep -rn "<<<<<<<\|\>>>>>>>" --include="*.py" .
sed -i '/^<<<<<<< /d' path/to/file.py
sed -i '/^=======$/d' path/to/file.py
sed -i '/^>>>>>>> /d' path/to/file.py
python3 -c "compile(open('path/to/file.py').read(), 'file.py', 'exec')"
```

### Prevention
- Use `hermes update` (not git pull) to update the agent
- Avoid `git stash`/`git merge` inside the agent directory
