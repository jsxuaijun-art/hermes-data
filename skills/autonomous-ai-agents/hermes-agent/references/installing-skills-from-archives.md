# Installing Skills from Archive Files (Zip / Tarball)

The standard `hermes skills install` command supports hub IDs and direct `SKILL.md` URLs,
but some vendors distribute skills as zip archives containing a complete skill directory.
This guide covers that workflow.

## When You Need This

- A third-party platform (like Tencent IMA, Feishu, DingTalk) distributes its skill as a `.zip`
- The skill contains sub-modules (`notes/`, `knowledge-base/`), scripts, and reference files
- The archive includes a `meta.json` with runtime requirements (e.g., `required_binaries`)

## Installation Workflow

```bash
# 1. Download the archive
curl -sL -o skill.zip "https://example.com/skills/skill-name-1.0.0.zip"

# 2. Inspect the structure
unzip -l skill.zip
# Expect: skill-name/SKILL.md, skill-name/meta.json, skill-name/ima_api.cjs, etc.

# 3. Extract
unzip -o skill.zip           # or: unzip -q skill.zip

# 4. Copy to Hermes skills directory
cp -r skill-name ~/.hermes/skills/skill-name

# 5. Check runtime requirements (from meta.json)
cat skill-name/meta.json | grep required_binaries

# 6. Verify installation
ls ~/.hermes/skills/skill-name/SKILL.md
ls ~/.hermes/skills/skill-name/ima_api.cjs   # if present
```

The skill is now available next time you start Hermes or call `/skill skill-name`.

## Requirements Check

After installation, verify any runtime dependencies listed in `meta.json`:

```bash
# Check Node.js (common requirement for many API-wrapper skills)
node --version   # Need 18+ per typical meta.json requirement
```

If missing, install without root (binary download):

```bash
# Install Node.js v20 LTS as user (no sudo needed)
curl -fsSL https://nodejs.org/dist/v20.18.0/node-v20.18.0-linux-x64.tar.xz -o /tmp/node.tar.xz
mkdir -p ~/.local/node
tar -xf /tmp/node.tar.xz -C ~/.local/node --strip-components=1
export PATH="$HOME/.local/node/bin:$PATH"
echo 'export PATH="$HOME/.local/node/bin:$PATH"' >> ~/.bashrc
```

## Credential Configuration

Skills that wrap third-party APIs typically need credentials. The two common patterns:

### Pattern A: Environment Variables

```bash
export IMA_OPENAPI_CLIENTID="your_client_id"
export IMA_OPENAPI_APIKEY="your_api_key"
```

Add to `~/.bashrc` for persistence.

### Pattern B: Credential Files

```bash
mkdir -p ~/.config/imasource
echo "your_client_id" > ~/.config/ima/client_id
echo "your_api_key" > ~/.config/ima/api_key
```

The exact path and file names depend on the skill. Check the skill's `SKILL.md` or
`ima_api.cjs` for the credential loading order (usually: env vars → config files).

## Multi-Module Skill Structure

Some advanced skills ship with sub-modules. Example (Tencent IMA):

```
ima-skill/
├── SKILL.md                   # Main dispatcher — routes between sub-modules
├── ima_api.cjs                # Shared API wrapper script (Node.js)
├── meta.json                  # Version + runtime requirements
├── notes/
│   ├── SKILL.md               # Notes sub-module
│   └── references/
│       └── api.md             # Notes API reference
└── knowledge-base/
    ├── SKILL.md               # Knowledge base sub-module
    ├── references/
    │   └── api.md             # KB API reference
    └── scripts/
        ├── preflight-check.cjs  # File type validation
        └── cos-upload.cjs       # COS (Tencent Cloud Object Storage) upload
```

In this pattern, `load SKILL.md` loads the main dispatch table, which then tells
the agent to read the appropriate sub-module's `SKILL.md` for implementation details.

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| Skill not found after install | Skill loaded before files were copied | Start a new session: `/new` or exit+relaunch |
| `node: command not found` | Node.js missing | Install via binary download (see above) |
| API call returns auth error | Credentials not configured | Check env vars or config files |
| Script exits with code -100 | Missing or invalid credentials | Re-check client ID / API key |
| Script exits with code -200 | Skill version update available | The script's stdout has update context JSON with instructions |

## Skill Updates

Some skills have built-in version checking (e.g., IMA skill checks once per day).
When an update is available, the API wrapper exits with code `-200` and outputs
update instructions to stdout. Follow those instructions, then re-install from
the updated archive.
