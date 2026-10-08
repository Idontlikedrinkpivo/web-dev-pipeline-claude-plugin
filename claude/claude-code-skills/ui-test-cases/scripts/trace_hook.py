#!/usr/bin/env python3
"""Claude Code PostToolUse hook: after the agent edits a test case, a screen spec, the frames register or the
OpenAPI, re-check every test case's «Трассировка». Broken references go back to the agent (exit 2)."""
import json, subprocess, sys
from pathlib import Path

WATCH = ("/ui/test-cases", "/test-cases.md", "/ui/screen-specs/", "frames-register.md", "/documentation/api/")

try:
    data = json.load(sys.stdin)
except Exception:
    sys.exit(0)
path = (data.get("tool_input") or {}).get("file_path") or ""
if "/documentation/" not in path or not any(w in path for w in WATCH):
    sys.exit(0)
docs = Path(path[: path.index("/documentation/") + len("/documentation")])
r = subprocess.run([sys.executable, str(Path(__file__).with_name("check_trace.py")), "--docs", str(docs), "--quiet"],
                   capture_output=True, text=True)
if r.returncode == 1:
    lines = r.stdout.strip().splitlines()
    print("Трассировка тест-кейсов разошлась с документами — исправь до того, как идти дальше "
          "(ui-test-cases → «Трассировка»; устаревшее ТЗ — его стадия):", file=sys.stderr)
    print("\n".join(lines[:25] + ([f"… и ещё {len(lines) - 25}"] if len(lines) > 25 else [])), file=sys.stderr)
    sys.exit(2)
sys.exit(0)
