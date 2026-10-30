"""Run a check (tests, lint, typecheck) with its full output in a file and a short summary on stdout.

    python3 run_check.py <name> -- <command and its arguments>

The orchestrator and the executors read the summary, not hundreds of lines of output: the exit code, how many
tests passed, failed and were skipped, the failing tests with the first lines of their errors, and the path of the
full log (under `<git dir>/pipeline-work/checks/`). What is dropped is decided here, not by the reader. When the
output cannot be parsed, or the command failed and no failing test was named, the summary prints the last 60
lines instead — more, never less.

The counts of the previous run with the same <name> are kept beside the log: fewer tests than last time, or more
skipped, is flagged «⚠» — a test that quietly disappeared or was switched off. Exit code: the command's own.
Recognised: Vitest / Jest, pytest, Playwright, tsc, ESLint, Ruff; anything else gets the exit code and the tail.
Standard library only.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ANSI = re.compile(r"\x1b\[[0-9;]*m")


def git_dir() -> Path:
    try:
        out = subprocess.run(["git", "rev-parse", "--absolute-git-dir"], capture_output=True, text=True).stdout.strip()
        if out:
            return Path(out)
    except OSError:
        pass
    return Path(".git")


def counts(text: str) -> dict:
    c: dict = {}
    # Vitest / Jest: "Tests  12 passed | 1 failed | 2 skipped (15)" or "Tests: 1 failed, 12 passed, 15 total"
    m = re.search(r"^\s*Tests:?\s+(.*)$", text, re.M)
    if m:
        for n, k in re.findall(r"(\d+)\s+(passed|failed|skipped|todo|pending)", m.group(1)):
            c[k] = c.get(k, 0) + int(n)
    # pytest: "=== 3 failed, 40 passed, 2 skipped in 1.2s ==="
    m = re.search(r"^=+ (.*?) in [\d.]+s", text, re.M)
    if m and not c:
        for n, k in re.findall(r"(\d+) (passed|failed|skipped|error|errors|xfailed|xpassed)", m.group(1)):
            c["failed" if k.startswith("error") else k] = c.get(k, 0) + int(n)
    # Playwright: "  12 passed (30s)", "  1 failed", "  2 skipped", "  1 flaky"
    if not c:
        for n, k in re.findall(r"^\s+(\d+) (passed|failed|skipped|flaky|did not run)\b", text, re.M):
            c[k] = c.get(k, 0) + int(n)
    # tsc: "Found 3 errors"; ESLint: "✖ 5 problems (3 errors, 2 warnings)"; Ruff: "Found 4 errors."
    m = re.search(r"Found (\d+) errors?", text)
    if m:
        c["errors"] = int(m.group(1))
    m = re.search(r"✖ (\d+) problems? \((\d+) errors?, (\d+) warnings?\)", text)
    if m:
        c["errors"], c["warnings"] = int(m.group(2)), int(m.group(3))
    return c


def failures(text: str) -> list[str]:
    pats = [r"^\s*(?:FAIL|×|✗|✘)\s+(.+)$", r"^FAILED (.+)$", r"^\s+\d+\) (\[[^\]]+\] › .+)$",
            r"^(.+\.(?:ts|tsx|js|py)\(\d+,\d+\): error .+)$", r"^(.+:\d+:\d+: \w+ .+)$"]
    found: list[str] = []
    for p in pats:
        for m in re.finditer(p, text, re.M):
            line = m.group(1).strip()[:240]
            if line not in found:
                found.append(line)
    return found[:30]


def main() -> None:
    args = sys.argv[1:]
    if len(args) < 3 or args[1] != "--":
        sys.exit(__doc__)
    name, cmd = re.sub(r"[^\w.-]", "_", args[0]), args[2:]
    folder = git_dir() / "pipeline-work" / "checks"
    folder.mkdir(parents=True, exist_ok=True)
    log = folder / f"{name}-{datetime.now():%Y%m%d-%H%M%S-%f}.log"
    proc = subprocess.run(cmd, capture_output=True, text=True, errors="replace")
    text = ANSI.sub("", (proc.stdout or "") + ("\n" + proc.stderr if proc.stderr else ""))
    log.write_text(f"$ {' '.join(cmd)}\n{text}", encoding="utf-8")
    c = counts(text)
    last_file = folder / f"{name}.last.json"
    try:
        last = json.loads(last_file.read_text())
    except (OSError, ValueError):
        last = {}
    total = sum(v for k, v in c.items() if k in ("passed", "failed", "skipped", "flaky", "todo", "xfailed", "xpassed"))
    warn = []
    if last.get("total") and total and total < last["total"]:
        warn.append(f"⚠ тестов стало меньше: было {last['total']}, стало {total}")
    if c.get("skipped", 0) > last.get("skipped", 0) and "skipped" in last:
        warn.append(f"⚠ пропущенных стало больше: было {last['skipped']}, стало {c['skipped']}")
    if total:
        last_file.write_text(json.dumps({"total": total, "skipped": c.get("skipped", 0)}))
    shown = " · ".join(f"{k} {v}" for k, v in c.items()) or "счётчиков не нашёл"
    print(f"{name}: код {proc.returncode} · {shown} · полный вывод: {log}")
    for w in warn:
        print(w)
    fails = failures(text) if proc.returncode or c.get("failed") or c.get("errors") else []
    for f in fails:
        print(f"  ✗ {f}")
    if (proc.returncode and not fails) or (not c and proc.returncode):
        print("— последние строки —")
        print("\n".join(text.rstrip().splitlines()[-60:]))
    sys.exit(proc.returncode)


if __name__ == "__main__":
    main()
