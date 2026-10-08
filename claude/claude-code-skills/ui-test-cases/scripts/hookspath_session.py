#!/usr/bin/env python3
"""Claude Code SessionStart hook: a project that ships .githooks/ (the test-case trace check) gets
core.hooksPath set once, so nobody has to remember the command. Never overrides another hooks setup."""
import json, subprocess, sys
from pathlib import Path

try:
    cwd = Path(json.load(sys.stdin).get("cwd") or ".")
except Exception:
    cwd = Path(".")
root = subprocess.run(["git", "-C", str(cwd), "rev-parse", "--show-toplevel"], capture_output=True, text=True).stdout.strip()
if not root or not (Path(root) / ".githooks" / "pre-commit").exists():
    sys.exit(0)
cur = subprocess.run(["git", "-C", root, "config", "--get", "core.hooksPath"], capture_output=True, text=True).stdout.strip()
if cur == ".githooks":
    sys.exit(0)
if cur:  # husky, lefthook or a custom path: leave it, the call lives in that hook instead
    sys.exit(0)
subprocess.run(["git", "-C", root, "config", "core.hooksPath", ".githooks"])
print("Подключил проверку трассировки тест-кейсов при коммите (git config core.hooksPath .githooks).")
