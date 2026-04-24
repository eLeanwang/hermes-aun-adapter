#!/usr/bin/env python3
"""AUN platform configuration — invoked by hermes_cli/setup.py via _setup_aun()."""

import asyncio
import os
import re

_AID_LABEL_RE = re.compile(r'^[a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?$')
_AUN_PATH = os.path.expanduser("~/.aun")


def _is_valid_aid(name: str) -> bool:
    labels = name.split('.')
    return len(labels) >= 3 and all(_AID_LABEL_RE.match(l) for l in labels)


def _ensure_aid(aid: str, print_info, print_success, print_error) -> str | None:
    """Check local keypair; create AID on gateway if missing.
    Returns the cert URL derived from the discovered gateway, or None on failure."""
    from aun_core import AUNClient
    from aun_core.keystore.file import FileKeyStore
    from urllib.parse import urlparse, urlunparse

    ks = FileKeyStore(_AUN_PATH)
    local = ks.load_identity(aid)

    async def _create_and_get_gateway():
        client = AUNClient({"aun_path": _AUN_PATH})
        # No _gateway_url set → SDK resolves via well-known discovery
        await client.auth.create_aid({"aid": aid})
        return client._gateway_url

    if local and "private_key_pem" in local:
        print_success(f"✓ Local keypair found for {aid}")
        print_info("  Resolving gateway via well-known discovery...")
        try:
            gateway_url = asyncio.run(_create_and_get_gateway())
        except Exception as e:
            print_error(f"Failed to resolve gateway: {e}")
            return None
    else:
        print_info(f"  AID {aid} not found locally — creating via SDK auto-discovery...")
        try:
            gateway_url = asyncio.run(_create_and_get_gateway())
            print_success(f"✓ AID created: {aid}")
        except Exception as e:
            print_error(f"Failed to create AID: {e}")
            return None

    # Derive cert URL from the actual discovered gateway (preserves port)
    parsed = urlparse(gateway_url)
    scheme = "https" if parsed.scheme == "wss" else "http"
    cert_url = urlunparse((scheme, parsed.netloc, f"/pki/cert/{aid}", "", "", ""))
    print_info(f"  Gateway: {gateway_url}")
    return cert_url


def _check_registered(cert_url: str, print_success, print_error, print_info) -> bool:
    """Verify AID is registered on the gateway. Returns True if reachable."""
    import urllib.request
    print_info(f"  Verifying: {cert_url}")
    try:
        urllib.request.urlopen(cert_url, timeout=5)
        print_success("✓ AID is registered on gateway")
        return True
    except Exception:
        print_error("AID not reachable on gateway")
        print_info(f"  Checked: {cert_url}")
        return False


def run(print_header, print_info, print_success, print_error, print_warning,
        prompt, prompt_yes_no, get_env_value, save_env_value):
    """Main setup flow — UI helpers injected from hermes_cli/setup.py."""
    print_header("AUN (Agent Union Network)")

    existing = get_env_value("AUN_AID")
    if existing:
        print_info(f"AUN: already configured (AID: {existing})")
        if not prompt_yes_no("Reconfigure AUN?", False):
            return

    print()
    print_info("AUN enables P2P agent communication via WebSocket + E2EE.")
    print()

    # aun-core must be installed first (SKILL.md step 1: run install.py)
    try:
        from aun_core import __version__ as _ver
        print_success(f"✓ aun-core: installed (v{_ver})")
    except ImportError:
        print_error("aun-core is not installed.")
        print_info("Run the AUN adapter install script first:")
        print_info("  python ~/.hermes/skills/aun-adapter/scripts/install.py")
        return

    print()
    print_info("Enter your AUN Agent ID (AID), e.g. hermes.agentid.pub")
    print_info("If the AID does not exist yet, it will be created automatically.")
    print()

    while True:
        aid = prompt("AUN Agent ID (AID)")
        if not aid or not aid.strip():
            print_warning("AUN setup cancelled (no AID provided)")
            return

        aid = aid.strip()

        if not _is_valid_aid(aid):
            print_error(f"Invalid AID format: {aid}")
            print_info("  Expected: <name>.<domain>.<tld>  (e.g. hermes.agentid.pub)")
            print_info("  Each label: letters, digits, hyphens; at least 3 labels")
            continue

        print()
        cert_url = _ensure_aid(aid, print_info, print_success, print_error)
        if not cert_url:
            continue

        if not _check_registered(cert_url, print_success, print_error, print_info):
            continue

        print()
        if prompt_yes_no("Use this AID?", True):
            break

    save_env_value("AUN_AID", aid)
    print_success(f"AUN_AID set to {aid}")

    owner = prompt("Owner AID (optional, leave empty to skip)")
    owner_aid = owner.strip() if owner else ""
    if owner_aid:
        save_env_value("AUN_OWNER_AID", owner_aid)
        print_success(f"AUN_OWNER_AID set to {owner_aid}")

    print()
    default_home = owner_aid or aid
    home = prompt(f"Home Channel AID (default: {default_home})")
    home_aid = home.strip() if home else ""
    if not home_aid:
        home_aid = default_home
    save_env_value("AUN_HOME_CHANNEL", home_aid)
    print_success(f"AUN_HOME_CHANNEL set to {home_aid}")

    print()
    print_success("✓ AUN configured successfully")
    print_info("  Gateway: resolved automatically at runtime via well-known discovery")
    print_info("  Start gateway: hermes gateway")
