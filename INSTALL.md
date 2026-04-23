# Installing AUN Adapter for Hermes

This document guides you through installing the AUN adapter skill into your Hermes instance.

## One-line Bootstrap

```bash
git clone git@github.com:eLeanwang/hermes-aun-adapter.git /tmp/hermes-aun-adapter && mkdir -p ~/.hermes/skills/aun-adapter && cp -r /tmp/hermes-aun-adapter/. ~/.hermes/skills/aun-adapter/ && rm -rf /tmp/hermes-aun-adapter && python ~/.hermes/skills/aun-adapter/scripts/install.py && echo "Done. Now read ~/.hermes/skills/aun-adapter/SKILL.md to complete Hermes source modifications."
```

After running, follow the prompt to read `SKILL.md` for the remaining source code steps.

---

## Prerequisites

- Hermes gateway installed and configured
- Python 3.11+
- `git` available in PATH
- `HERMES_PROJECT_PATH` env var set, or Hermes located at `~/projects/hermes-agent`

## Step 1: Download the skill

Run the following commands to clone this repo and install the skill:

```bash
# Clone to a temporary location
git clone https://github.com/eLeanwang/hermes-aun-adapter.git /tmp/hermes-aun-adapter

# Create skill directory and copy files
mkdir -p ~/.hermes/skills/aun-adapter
cp -r /tmp/hermes-aun-adapter/. ~/.hermes/skills/aun-adapter/

# Clean up
rm -rf /tmp/hermes-aun-adapter

echo "Skill files installed to ~/.hermes/skills/aun-adapter/"
```

## Step 2: Run the install script

The install script handles:
- Installing the `aun-core` Python package
- Copying the adapter template to your Hermes project

```bash
python ~/.hermes/skills/aun-adapter/scripts/install.py
```

Expected output:
```
=== AUN Adapter Manager ===

Hermes project: /path/to/hermes-agent

--- Installing ---

✓ aun-core: already installed
✓ Adapter placed: /path/to/hermes-agent/gateway/platforms/aun.py

Files placed successfully.
```

If it says "AUN adapter is already installed", choose `r` to reinstall.

## Step 3: Verify the download

```bash
python ~/.hermes/skills/aun-adapter/scripts/check.py
```

At this stage, only `aun_core_importable` and `aun_adapter_file` should be `true`. The rest require manual source code modifications — see the next step.

## Step 4: Apply source code modifications

Read `~/.hermes/skills/aun-adapter/SKILL.md` and follow the **Install** section to modify Hermes source code (8 insertion points across 3 files).

```bash
# View the full installation guide
cat ~/.hermes/skills/aun-adapter/SKILL.md
```

After completing all modifications, run the check again — all 11 checks should pass (except `aun_aid_configured` which requires `AUN_AID` to be set in your `.env`).

## Step 5: Configure your AUN identity

Add to `~/.hermes/.env`:

```bash
AUN_AID=your-agent-id.agentid.pub
# Optional:
AUN_OWNER_AID=owner.agentid.pub
AUN_ALLOWED_USERS=trusted1.agentid.pub,trusted2.agentid.pub
```

Then restart the Hermes gateway:

```bash
hermes gateway start
```

## Troubleshooting

**"Cannot find hermes-agent project"**
Set the environment variable:
```bash
export HERMES_PROJECT_PATH=/path/to/your/hermes-agent
python ~/.hermes/skills/aun-adapter/scripts/install.py
```

**Check fails after Hermes upgrade**
A `git pull` on Hermes will overwrite the manual source modifications. Re-apply them by running:
```bash
python ~/.hermes/skills/aun-adapter/scripts/check.py
```
Then fix each failed check per the SKILL.md Repair section.

**aun-core install fails**
Install manually:
```bash
pip install aun-core
# or with uv:
uv pip install aun-core
```
