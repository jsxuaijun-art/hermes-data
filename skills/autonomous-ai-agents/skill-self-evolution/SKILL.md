---
name: skill-self-evolution
description: Use hermes-agent-self-evolution to optimize Hermes Agent skills via DSPy MIPROv2/GEPA optimization. Covers setup, execution, troubleshooting, and interpretation of evolution results.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [hermes, skills, evolution, optimization, dspy, self-improvement]
    related_skills: [hermes-agent, corporate-tax-planning, workbuddy-output]
trigger: >
  User asks to "evolve" a skill, "optimize" a skill using the self-evolution toolbox,
  "run the evolution pipeline", or mentions hermes-agent-self-evolution.
  Also triggers when the user wants to improve skill quality through automated optimization.
---

# Skill Self-Evolution

This skill covers the complete workflow for using `hermes-agent-self-evolution` to
optimize Hermes Agent skills. The tool uses DSPy (MIPROv2 or GEPA) to find optimal
instruction prompts and few-shot examples for a skill, evaluated against a synthetic
or real dataset.

## Overview

```
hermes-agent-self-evolution/
├── evolution/
│   └── skills/
│       ├── evolve_skill.py     ← Main entry point
│       └── output/             ← Evolution results
├── datasets/                   ← Generated training data
├── venv/                       ← Isolated Python venv
└── requirements/               ← Pip deps
```

The optimizer runs multiple trials, each evaluating instruction+fewshot combinations
on a held-out validation set. Best combination is returned.

---

## Setup

### 1. Clone the repo

```bash
git clone https://github.com/NousResearch/hermes-agent-self-evolution.git
cd hermes-agent-self-evolution
```

### 2. Create venv & install

```bash
python3 -m venv venv
source venv/bin/activate

# Standard install (may be slow on flaky networks)
pip install -e ".[dev]"

# 🔴 CHINA / FLASY NETWORK: Tsinghua mirror (reliable in WSL China)
pip install -e ".[dev]" -i https://pypi.tuna.tsinghua.edu.cn/simple --trusted-host pypi.tuna.tsinghua.edu.cn

# 🔴 Required for MIPROv2 optimization: dspy[optuna]
pip install "dspy[optuna]" -i https://pypi.tuna.tsinghua.edu.cn/simple --trusted-host pypi.tuna.tsinghua.edu.cn
```

**⚠️ Pitfall**: Without `dspy[optuna]`, MIPROv2 fails with `ModuleNotFoundError: No module named 'optuna'`.

### 3. Set `HERMES_AGENT_REPO`

The evolution script looks for skills in `$HERMES_AGENT_REPO/skills/`:

```bash
export HERMES_AGENT_REPO=/path/to/hermes-agent
```

---

## Skill Placement

The evolution script uses `Path.rglob("SKILL.md")` under `$HERMES_AGENT_REPO/skills/`
to find skills. **This does NOT follow symlinks.**

### Copy the skill (don't symlink)

```bash
# ❌ WRONG: symlink — silently ignored by rglob
ln -s ~/.hermes/skills/tax-planning/corporate-tax-planning $HERMES_AGENT_REPO/skills/

# ✅ RIGHT: copy the skill directory
cp -r ~/.hermes/skills/<category>/<skill-name> $HERMES_AGENT_REPO/skills/<skill-name>
```

---

## API Key Setup

The evolution tool runs in its own venv and does **not** automatically load
Hermes' `.env` file. You must source it manually.

### For DeepSeek (or other providers)

```bash
# Load ALL Hermes API keys into the environment
set -a && source ~/.hermes/.env && set +a

# Verify
echo $DEEPSEEK_API_KEY  # should print sk-... (not empty)
```

**⚠️ Pitfall**: If you don't source the .env, you'll get `Key not found for provider: deepseek`.
Exporting individual vars also works but sourcing the whole .env is more reliable.

---

## Running the Evolution

### Quick start

```bash
cd /path/to/hermes-agent-self-evolution
source venv/bin/activate
set -a && source ~/.hermes/.env && set +a
export HERMES_AGENT_REPO=/path/to/hermes-agent

python -m evolution.skills.evolve_skill \
  --skill <skill-name> \
  --iterations 5 \
  --optimizer-model deepseek/deepseek-chat \
  --eval-model deepseek/deepseek-chat
```

### Dry run (validate setup first)

```bash
python -m evolution.skills.evolve_skill \
  --skill <skill-name> \
  --dry-run \
  --optimizer-model deepseek/deepseek-chat \
  --eval-model deepseek/deepseek-chat
```

This generates the dataset and validates setup without running full optimization.
Takes ~10-30 seconds.

### Key flags

| Flag | Purpose | Example |
|------|---------|---------|
| `--skill NAME` | Skill to evolve (required) | `--skill corporate-tax-planning` |
| `--iterations N` | MIPROv2 iterations (5 = ~10 trials) | `--iterations 5` |
| `--optimizer-model M` | Model that proposes instructions | `--optimizer-model deepseek/deepseek-chat` |
| `--eval-model M` | Model that evaluates proposals | `--eval-model deepseek/deepseek-chat` |
| `--dry-run` | Validate + generate dataset only | `--dry-run` |
| `--eval-source real` | Use real sessions (vs synthetic) | Needs session data |

---

## What to Expect

### Timeline

- Dataset generation: ~10s (20 synthetic examples)
- Bootstrapping (6 sets): ~45s
- Instruction proposal: ~30s (3 candidates)
- Optimizer trials: ~30-90s each × 10-11 trials
- **Total: ~7-8 minutes for 5 iterations**

### Score interpretation

MIPROv2 scores on a 0-100 scale. Typical baseline for well-written skills:

| Score | Meaning |
|-------|---------|
| 30% | Normal baseline for a well-written skill (evaluation is strict) |
| +1-5% above baseline | Optimization worked slightly |
| +10%+ | Skill had obvious instruction-level weaknesses |

Scores are relative — the evaluation model scores the DSPy program output
against `expected_behavior` fields in the training dataset.

### GEPA vs MIPROv2

The tool tries GEPA (genetic programming) first. If your DSPy version doesn't
support the `max_steps` parameter:

```
GEPA not available (GEPA.__init__() got an unexpected keyword argument 'max_steps'),
falling back to MIPROv2
```

This is **normal** — MIPROv2 is the stable default.

---

## Results

### Output location

```
output/<skill-name>/evolved_FAILED.md
```

### Constraint validation

The tool validates the evolved artifact against constraints:

| Constraint | What it checks | Common failure |
|------------|----------------|----------------|
| `size_limit` | Artifact ≤ 15,000 chars | Rare — skills are usually 4-8KB |
| `growth_limit` | Growth ≤ +20% | Rare if skill is already complete |
| `non_empty` | Artifact has content | Never fails if dataset works |
| `skill_structure` | Has YAML `---` frontmatter + name/description | **⚠️ Commonly fails!** |

**🔴 Critical nuance**: The constraint validation checks the DSPy program's output
artifact, NOT the final `evolved_FAILED.md` file. Even if validation says
`✗ skill_structure: Skill missing: YAML frontmatter`, the saved file may
have proper frontmatter (because the tool wraps the artifact into a complete
SKILL.md during save). The `evolved_FAILED.md` file is still valid and usable.

### If constraints fail

The tool saves the evolved skill as `evolved_FAILED.md` instead of auto-deploying.
This is intentional — the file IS the evolved skill, it just wasn't auto-copied.

To deploy manually:
```bash
cp output/<skill-name>/evolved_FAILED.md ~/.hermes/skills/<category>/<skill-name>/SKILL.md
```

Or simply inspect the diff to see what changed:
```bash
diff $HERMES_AGENT_REPO/skills/<skill-name>/SKILL.md output/<skill-name>/evolved_FAILED.md
```

### No-change outcome

If the original skill is already well-optimized, the evolved output may be
**byte-identical** to the input (growth = 0%). This is a **positive signal** —
it means the skill's instruction design is already near-optimal and the
optimization confirmed it.

### To get better results

1. **Use real session data**: `--eval-source real` uses past Hermes sessions
   where the skill was loaded, rather than synthetic examples
2. **Increase iterations**: `--iterations 10` runs more trials
3. **Try different eval models**: Stronger models often give finer-grained
   evaluation signals
4. **Post-process manually**: Review the evolved_FAILED.md for any prompt
   wording improvements even if the score didn't change much

---

## Pitfalls

### 1. Symlinks are silently ignored
`Path.rglob("SKILL.md")` doesn't follow symlinks. Always **copy** the skill
into `$HERMES_AGENT_REPO/skills/`.

### 2. API keys not inherited
The venv doesn't auto-load `~/.hermes/.env`. Must `set -a && source` before
running the evolution command. Reset with `set +a` afterward.

### 3. Optuna required for MIPROv2
Basic `pip install -e ".[dev]"` may not include `dspy[optuna]`. Install
explicitly.

### 4. GEPA version mismatch
GEPA's `__init__` signature changed between DSPy versions. If you see the
"Unexpected keyword argument" fallback message, it's not a real error.

### 5. Constraint failure ≠ bad output
The `evolved_FAILED.md` suffix is from artifact-level validation, not
content quality. Always inspect the actual diff before discarding.

### 6. WSL SSL issues
Git clone and pip install may time out with SSL errors. Use Tsinghua mirror
for pip (`-i https://pypi.tuna.tsinghua.edu.cn/simple`) and SSH for git
(`git@github.com:...` instead of HTTPS).

### 7. Evaluate score meaning
The 30% baseline is NORMAL for this tool — it's evaluating strict format
adherence. Don't expect 90%+ scores. A +1-2% improvement with no content
regression is a success.

---

## References

- [Hermes Agent Self-Evolution GitHub](https://github.com/NousResearch/hermes-agent-self-evolution)
- [DSPy MIPROv2 Documentation](https://dspy.ai/optimization/miprov2/)
- [Hermes Agent Skills documentation](https://hermes-agent.nousresearch.com/docs/user-guide/features/skills)
