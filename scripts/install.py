#!/usr/bin/env python3
"""AUN adapter installer/uninstaller.

First run: installs aun-core dependency and places adapter file.
Subsequent runs: prompts to reinstall, uninstall, or exit.
Code modifications to hermes are done by the agent following SKILL.md instructions."""

import os
import shutil
import subprocess
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

    print("ERROR: Cannot find hermes-agent project.")
    print("Set HERMES_PROJECT_PATH environment variable to the project root.")
    sys.exit(1)


def install_aun_core() -> bool:
    """Install aun-core from PyPI. Returns True on success."""
    try:
        import aun_core  # noqa: F401
        print("\u2713 aun-core: already installed")
        return True
    except ImportError:
        pass

    print("Installing aun-core...")
    uv_bin = shutil.which("uv")
    if uv_bin:
        result = subprocess.run(
            [uv_bin, "pip", "install", "--python", sys.executable, "aun-core"],
            capture_output=True, text=True,
        )
    else:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "aun-core"],
            capture_output=True, text=True,
        )

    if result.returncode == 0:
        print("\u2713 aun-core: installed")
        return True
    else:
        print("\u2717 aun-core: install failed")
        if result.stderr:
            last_line = result.stderr.strip().splitlines()[-1]
            print(f"  Error: {last_line}")
        return False


def place_adapter_file(hermes_path: Path) -> bool:
    """Copy templates/aun.py -> gateway/platforms/aun.py."""
    skill_dir = Path(__file__).parent.parent
    src = skill_dir / "templates" / "aun.py"
    dst = hermes_path / "gateway" / "platforms" / "aun.py"

    if not src.exists():
        print(f"\u2717 Template not found: {src}")
        return False

    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    print(f"\u2713 Adapter placed: {dst}")
    return True


def remove_adapter_file(hermes_path: Path):
    """Remove gateway/platforms/aun.py."""
    aun_file = hermes_path / "gateway" / "platforms" / "aun.py"
    if aun_file.exists():
        aun_file.unlink()
        print(f"\u2713 Removed: {aun_file}")
    else:
        print(f"- Not found (already removed): {aun_file}")


def is_installed(hermes_path: Path) -> bool:
    """Check if adapter file is already placed."""
    return (hermes_path / "gateway" / "platforms" / "aun.py").is_file()


def do_install(hermes_path: Path):
    """Run install flow."""
    print("--- Installing ---\n")

    dep_ok = install_aun_core()
    file_ok = place_adapter_file(hermes_path)

    print()
    if dep_ok and file_ok:
        print("Files placed successfully.")
        print("Agent should now modify hermes code per SKILL.md instructions:")
        print("  1. Add Platform.AUN to gateway/config.py")
        print("  2. Add AUN branch to gateway/run.py _create_adapter()")
        print("  3. Add AUN to platform_env_map and platform_allow_all_map")
        print("  4. Add AUN env override to gateway/config.py _apply_env_overrides()")
        print("  5. Add _setup_aun() to hermes_cli/setup.py")
    else:
        print("Installation incomplete \u2014 fix errors above and retry.")
        sys.exit(1)


def do_uninstall(hermes_path: Path):
    """Run uninstall flow."""
    print("--- Uninstalling ---\n")

    remove_adapter_file(hermes_path)

    print()
    print("Agent should now remove AUN references from hermes code:")
    print("  1. Remove Platform.AUN from gateway/config.py")
    print("  2. Remove AUN branch from gateway/run.py _create_adapter()")
    print("  3. Remove AUN from platform_env_map and platform_allow_all_map")
    print("  4. Remove AUN env override from gateway/config.py _apply_env_overrides()")
    print("  5. Remove _setup_aun() from hermes_cli/setup.py")


def prompt_choice() -> str:
    """Prompt user for action when already installed."""
    print("AUN adapter is already installed.\n")
    print("  [r] Reinstall (overwrite adapter file)")
    print("  [u] Uninstall (remove adapter file)")
    print("  [q] Quit")
    print()
    while True:
        choice = input("Choose [r/u/q]: ").strip().lower()
        if choice in ("r", "u", "q"):
            return choice
        print("Invalid choice. Enter r, u, or q.")


def main():
    print("=== AUN Adapter Manager ===\n")

    hermes_path = find_hermes_project()
    print(f"Hermes project: {hermes_path}\n")

    if is_installed(hermes_path):
        choice = prompt_choice()
        if choice == "r":
            do_install(hermes_path)
        elif choice == "u":
            do_uninstall(hermes_path)
        else:
            print("Exiting.")
    else:
        do_install(hermes_path)


if __name__ == "__main__":
    main()
