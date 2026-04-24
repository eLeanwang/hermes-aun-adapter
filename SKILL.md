---
name: aun-adapter
description: AUN (Agent Union Network) platform adapter for hermes gateway. Install, check, repair, and upgrade the AUN adapter that enables P2P agent-to-agent communication.
version: 1.0.0
author: EvolClaw
platforms: [linux, macos]
required_environment_variables:
  - name: AUN_AID
    prompt: "Your Agent ID (e.g. hermes.agentid.pub)"
metadata:
  hermes:
    tags: [AUN, gateway, adapter, networking, P2P, agent-communication]
---

# AUN Adapter

P2P agent-to-agent communication via the AUN (Agent Union Network) protocol.
AUN uses WebSocket + E2EE for secure, decentralized agent messaging.

## Operations

### Install

Run the following steps in order:

1. **Run the install script** to install the `aun-core` dependency and place the adapter file:

   ```bash
   python ~/.hermes/skills/aun-adapter/scripts/install.py
   ```

2. **Modify hermes source code** — read each target file, find the correct insertion point, and add the AUN registration code:

   **a) `gateway/config.py` — Add `AUN` to the `Platform` enum:**
   Find `class Platform(Enum)` and add after the last member (currently `QQBOT`):
   ```python
       AUN = "aun"
   ```

   **b) `gateway/config.py` — Add AUN block to `_apply_env_overrides()`:**
   Find the `_apply_env_overrides()` function. After the last platform block (currently QQBOT), before the `# Session settings` comment, add:
   ```python
       # AUN (Agent Union Network)
       aun_aid = os.getenv("AUN_AID", "").strip()
       if aun_aid:
           owner_aid = os.getenv("AUN_OWNER_AID", "").strip() or None
           if Platform.AUN not in config.platforms:
               config.platforms[Platform.AUN] = PlatformConfig()
           config.platforms[Platform.AUN].enabled = True
           config.platforms[Platform.AUN].extra.update({
               "aid": aun_aid,
               "owner_aid": owner_aid,
           })
   ```

   **c) `gateway/run.py` — Add AUN branch to `_create_adapter()`:**
   Find the `_create_adapter()` method. After the last `elif platform == Platform.XXX:` branch (currently QQBOT), before `return None`, add:
   ```python
           elif platform == Platform.AUN:
               from gateway.platforms.aun import AunAdapter, check_aun_requirements
               if not check_aun_requirements():
                   logger.warning("AUN: aun-core not installed or AUN_AID not set")
                   return None
               return AunAdapter(config)
   ```

   **d) `gateway/run.py` — Add AUN to `platform_env_map`:**
   Find `platform_env_map = {` in `_is_user_authorized()`. After the last entry, add:
   ```python
               Platform.AUN: "AUN_ALLOWED_USERS",
   ```

   **e) `gateway/run.py` — Add AUN to `platform_allow_all_map`:**
   Find `platform_allow_all_map = {` in `_is_user_authorized()`. After the last entry, add:
   ```python
               Platform.AUN: "AUN_ALLOW_ALL_USERS",
   ```

   **f) `gateway/run.py` — Add AUN to `_get_unauthorized_dm_behavior()` map:**
   Find the second `platform_env_map = {` inside the `_get_unauthorized_dm_behavior()` method (around line 3068). After the last entry, add:
   ```python
               Platform.AUN: "AUN_ALLOWED_USERS",
   ```

   **g) `hermes_cli/setup.py` — Add `_setup_aun()` function:**
   Add this thin delegator before the `_GATEWAY_PLATFORMS` list definition. All setup logic lives in the skill-owned `scripts/config.py` so hermes source stays minimal:
   ```python
   def _setup_aun():
       """Configure AUN (Agent Union Network) platform."""
       import importlib.util, os
       _skill_config = os.path.expanduser("~/.hermes/skills/aun-adapter/scripts/config.py")
       if not os.path.exists(_skill_config):
           print_error("AUN skill not installed. Run:")
           print_info("  python ~/.hermes/skills/aun-adapter/scripts/install.py")
           return
       spec = importlib.util.spec_from_file_location("aun_config", _skill_config)
       mod = importlib.util.module_from_spec(spec)
       spec.loader.exec_module(mod)
       mod.run(print_header, print_info, print_success, print_error, print_warning,
               prompt, prompt_yes_no, get_env_value, save_env_value)
   ```

   **h) `hermes_cli/setup.py` — Register in `_GATEWAY_PLATFORMS`:**
   Find the `_GATEWAY_PLATFORMS = [` list. Before the closing `]`, add:
   ```python
       ("AUN (Agent Union Network)", "AUN_AID", _setup_aun),
   ```

   **i) `hermes_cli/setup.py` — Add to `any_messaging` check:**
   Find the `any_messaging = (` expression. Before the closing `)`, add:
   ```python
           or get_env_value("AUN_AID")
   ```

   **j) `hermes_cli/platforms.py` — Add AUN to `PLATFORMS` registry:**
   Find the `PLATFORMS: OrderedDict` definition. After the `qqbot` entry, before `webhook`, add:
   ```python
       ("aun",            PlatformInfo(label="🔗 AUN",             default_toolset="hermes-aun")),
   ```

   **k) `gateway/run.py` — Add `AUN_ALLOWED_USERS` to `_any_allowlist` check:**
   Find the `_any_allowlist = any(` block (around the gateway startup section). After the last `*_ALLOWED_USERS` entry (currently `QQ_ALLOWED_USERS`), before `GATEWAY_ALLOWED_USERS`, add:
   ```python
                       "AUN_ALLOWED_USERS",
   ```

   **l) `gateway/run.py` — Add `AUN_ALLOW_ALL_USERS` to `_allow_all` check:**
   Find the `_allow_all = ` block immediately after `_any_allowlist`. After the last `*_ALLOW_ALL_USERS` entry (currently `QQ_ALLOW_ALL_USERS`), add:
   ```python
                       "AUN_ALLOW_ALL_USERS")
   ```
   (Replace the closing `)` on the previous line with a comma and add this new last entry.)

   **m) `hermes_cli/status.py` — Add AUN to Messaging Platforms display:**
   Find the `platforms = {` dict in the Messaging Platforms section. After the `"QQBot"` entry, before the closing `}`, add:
   ```python
           "AUN": ("AUN_AID", "AUN_HOME_CHANNEL"),
   ```

3. **Verify installation** by running the check script:

   ```bash
   python ~/.hermes/skills/aun-adapter/scripts/check.py
   ```

   All checks should pass (except `aun_aid_configured` which requires the user to set AUN_AID in `.env`).

### Check

Run the integrity check to verify all AUN adapter components are properly installed:

```bash
python ~/.hermes/skills/aun-adapter/scripts/check.py
```

Review the JSON output. Each check should be `true`. If any are `false`, use the **Repair** operation.

### Repair

When checks fail (e.g. after a hermes upgrade overwrites registration code):

1. Run the check script to identify which components are broken:
   ```bash
   python ~/.hermes/skills/aun-adapter/scripts/check.py
   ```

2. For each failed check, re-apply the corresponding modification from the **Install** section above. Read the current version of each file first to find the correct insertion point — the code structure may have changed since the original install.

3. Run the check script again to verify all issues are resolved:
   ```bash
   python ~/.hermes/skills/aun-adapter/scripts/check.py
   ```

### Uninstall

1. **Run the install script** and choose uninstall:

   ```bash
   python ~/.hermes/skills/aun-adapter/scripts/install.py
   ```

   Select `u` when prompted to remove the adapter file.

2. Remove all AUN-related code from hermes source files — reverse each modification listed in the Install section:
   - Remove `AUN = "aun"` from `Platform` enum in `gateway/config.py`
   - Remove AUN env override block from `_apply_env_overrides()` in `gateway/config.py`
   - Remove AUN branch from `_create_adapter()` in `gateway/run.py`
   - Remove `Platform.AUN` entries from `platform_env_map` and `platform_allow_all_map` in `gateway/run.py`
   - Remove `AUN_ALLOWED_USERS` from `_any_allowlist` check and `AUN_ALLOW_ALL_USERS` from `_allow_all` check in `gateway/run.py`
   - Remove `_setup_aun()` function, `_GATEWAY_PLATFORMS` entry, and `any_messaging` AUN line from `hermes_cli/setup.py`
   - Remove `("aun", ...)` entry from `PLATFORMS` in `hermes_cli/platforms.py`
   - Remove `"AUN"` entry from `platforms` dict in `hermes_cli/status.py`

3. Optionally remove AUN environment variables from `~/.hermes/.env`:
   - `AUN_AID`, `AUN_OWNER_AID`, `AUN_HOME_CHANNEL`, `AUN_ALLOWED_USERS`, `AUN_ALLOW_ALL_USERS`
