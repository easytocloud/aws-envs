"""
aws-envs-setup: one-time migration from a single ~/.aws setup to a multi-environment aws-envs structure.

Run with:  uvx aws-envs-setup
"""

from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path


AWS_DIR = Path.home() / ".aws"
ENVS_DIR = AWS_DIR / "aws-envs"
DEFAULT_ENV_FILE = Path.home() / ".awsdefaultenv"


def _log(msg: str) -> None:
    print(f"aws-envs-setup: {msg}")


def _die(msg: str) -> None:
    print(f"aws-envs-setup ERROR: {msg}", file=sys.stderr)
    sys.exit(1)


def _ask(prompt: str, default: str) -> str:
    try:
        answer = input(f"{prompt} [{default}]: ").strip()
    except (EOFError, KeyboardInterrupt):
        print()
        _die("Aborted.")
    return answer if answer else default


def main() -> None:
    # Guard: already migrated?
    if ENVS_DIR.exists():
        _die(
            f"{ENVS_DIR} already exists — looks like you're already set up.\n"
            "To add a new environment use:  ase --init <name>"
        )

    config = AWS_DIR / "config"
    credentials = AWS_DIR / "credentials"

    if config.is_symlink() or credentials.is_symlink():
        _die(
            "~/.aws/config or ~/.aws/credentials is already a symlink.\n"
            "Refusing to migrate an already-converted setup."
        )

    if not config.exists() and not credentials.exists():
        print(
            "No ~/.aws/config or ~/.aws/credentials found.\n"
            "Nothing to migrate — creating an empty first environment instead."
        )

    env_name = _ask(
        "Name for your first environment (typically your AWS organization name)",
        "default",
    )

    env_dir = ENVS_DIR / env_name
    _log(f"Creating {env_dir}")
    env_dir.mkdir(parents=True, exist_ok=True)

    for fname in ("config", "credentials"):
        src = AWS_DIR / fname
        dst = env_dir / fname
        if src.exists():
            _log(f"Moving {src} -> {dst}")
            shutil.move(str(src), dst)
        else:
            _log(f"No {src} found — creating empty {dst}")
            dst.touch()

        _log(f"Symlinking {src} -> {dst}")
        src.symlink_to(dst)

    if DEFAULT_ENV_FILE.exists():
        _log(f"~/.awsdefaultenv already exists ({DEFAULT_ENV_FILE.read_text().strip()}) — leaving it unchanged")
    else:
        _log(f"Writing {DEFAULT_ENV_FILE} with environment '{env_name}'")
        DEFAULT_ENV_FILE.write_text(env_name + "\n")

    print()
    print("Setup complete!")
    print()
    print("Next step: install the oh-my-easytocloud plugin for oh-my-zsh to get the")
    print("  ase  (switch environment)  and  asp  (switch profile)  shell functions.")
    print()
    print("  https://github.com/easytocloud/oh-my-easytocloud")
    print()
    print("Open a new shell (or reload your zsh config) to activate the environment.")
