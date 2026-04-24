#!/usr/bin/env python3
"""Check AUN adapter installation integrity.

Outputs a JSON report with pass/fail for each check point.
Used by the agent to decide what needs repair after hermes upgrades."""

import importlib
import json
import os
import re
import sys
from pathlib import Path


def find_hermes_project() -> Path:
    """Locate hermes-agent project root."""
    env_path = os.getenv("HERMES_PROJECT_PATH")
    if env_path:
        p = Path(env_path)
        if (p / "gateway" / "platforms").is_dir():
            return p
    candidates = [
        Path.home() / "projects" / "hermes-agent",
        Path.home() / ".hermes" / "hermes-agent",
        Path.home() / "hermes-agent",
        Path("/opt/hermes-agent"),
    ]
    for c in candidates:
        if (c / "gateway" / "platforms").is_dir():
            return c
    try:
        import gateway
        return Path(gateway.__file__).parent.parent
    except ImportError:
        pass
    return Path(".")


def check_import(module_name: str) -> bool:
    """Check if a Python module is importable."""
    try:
        importlib.import_module(module_name)
        return True
    except ImportError:
        return False


def check_file_exists(hermes_path: Path, rel_path: str) -> bool:
    """Check if a file exists in the hermes project."""
    return (hermes_path / rel_path).is_file()


def check_file_contains(hermes_path: Path, rel_path: str, pattern: str) -> bool:
    """Check if a file contains a regex pattern."""
    filepath = hermes_path / rel_path
    if not filepath.is_file():
        return False
    content = filepath.read_text()
    return bool(re.search(pattern, content))


def check_all() -> dict:
    """Run all integrity checks."""
    hermes_path = find_hermes_project()
    results = {}

    # 1. aun-core importable
    results["aun_core_importable"] = check_import("aun_core")

    # 2. Adapter file exists
    results["aun_adapter_file"] = check_file_exists(
        hermes_path, "gateway/platforms/aun.py"
    )

    # 3. Platform.AUN in enum
    results["platform_enum"] = check_file_contains(
        hermes_path, "gateway/config.py", r'AUN\s*=\s*["\']aun["\']'
    )

    # 4. _create_adapter has AUN branch
    results["create_adapter_branch"] = check_file_contains(
        hermes_path, "gateway/run.py", r"Platform\.AUN"
    )

    # 5. platform_env_map has AUN
    results["env_map_entry"] = check_file_contains(
        hermes_path, "gateway/run.py", r'Platform\.AUN:\s*["\']AUN_ALLOWED_USERS["\']'
    )

    # 6. platform_allow_all_map has AUN
    results["allow_all_map_entry"] = check_file_contains(
        hermes_path,
        "gateway/run.py",
        r'Platform\.AUN:\s*["\']AUN_ALLOW_ALL_USERS["\']',
    )

    # 7. _apply_env_overrides has AUN block
    results["env_overrides"] = check_file_contains(
        hermes_path, "gateway/config.py", r'AUN_AID'
    )

    # 8. _setup_aun function exists
    results["setup_function"] = check_file_contains(
        hermes_path, "hermes_cli/setup.py", r"def _setup_aun\("
    )

    # 9. _GATEWAY_PLATFORMS includes AUN
    results["gateway_platforms_list"] = check_file_contains(
        hermes_path, "hermes_cli/setup.py", r"_setup_aun"
    )

    # 10. any_messaging includes AUN_AID
    results["any_messaging_check"] = check_file_contains(
        hermes_path, "hermes_cli/setup.py", r'AUN_AID'
    )

    # 11. hermes_cli/platforms.py has AUN entry
    results["platforms_registry"] = check_file_contains(
        hermes_path, "hermes_cli/platforms.py", r'"aun"'
    )

    # 12. _any_allowlist includes AUN_ALLOWED_USERS
    results["any_allowlist_entry"] = check_file_contains(
        hermes_path, "gateway/run.py", r'"AUN_ALLOWED_USERS"'
    )

    # 13. _allow_all includes AUN_ALLOW_ALL_USERS
    results["allow_all_entry"] = check_file_contains(
        hermes_path, "gateway/run.py", r'"AUN_ALLOW_ALL_USERS"'
    )

    # 14. hermes_cli/status.py has AUN entry
    results["status_display"] = check_file_contains(
        hermes_path, "hermes_cli/status.py", r'"AUN"'
    )

    # 15. AUN_AID configured in environment
    results["aun_aid_configured"] = bool(os.getenv("AUN_AID"))

    all_passed = all(results.values())
    return {
        "status": "ok" if all_passed else "issues_found",
        "hermes_path": str(hermes_path),
        "checks": results,
    }


def main():
    report = check_all()
    print(json.dumps(report, indent=2))

    # Human-readable summary
    print()
    checks = report["checks"]
    for name, passed in checks.items():
        icon = "\u2713" if passed else "\u2717"
        print(f"  {icon} {name}")
    print()
    if report["status"] == "ok":
        print("All checks passed.")
    else:
        failed = [k for k, v in checks.items() if not v]
        print(f"Issues found: {', '.join(failed)}")
    sys.exit(0 if report["status"] == "ok" else 1)


if __name__ == "__main__":
    main()
