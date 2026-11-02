#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Shannon's findings as one table — the input of security-audit's live check, Step 5
(references/live-pentest.md → 4).

    python3 shannon_report.py <report.sarif>

Reads the SARIF 2.1.0 log Shannon writes at its workspace's root and prints a Markdown table: number, rule (its id
and short name), level, place (file:line, or the URL when the finding has no code location), what it says, and
whether it was exploited — read from the result's properties (`status: exploited`, `exploited: true`) or its tags.
Then one line with the counts. The session takes each exploited row to its own check on the stand before it becomes
an F-row of the audit; this script decides nothing. Standard library only.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path


def place(result: dict) -> str:
    for loc in result.get("locations") or []:
        phys = loc.get("physicalLocation") or {}
        uri = (phys.get("artifactLocation") or {}).get("uri", "")
        line = (phys.get("region") or {}).get("startLine")
        if uri:
            return f"{uri}:{line}" if line else uri
    for loc in result.get("relatedLocations") or []:
        uri = ((loc.get("physicalLocation") or {}).get("artifactLocation") or {}).get("uri", "")
        if uri:
            return uri
    return (result.get("webRequest") or {}).get("target", "") or "—"   # a finding on the URL, not in the code


def exploited(result: dict) -> bool:
    props = result.get("properties") or {}
    status = str(props.get("status", "")).lower()
    tags = [str(t).lower() for t in props.get("tags") or []]
    return status == "exploited" or props.get("exploited") is True or "exploited" in tags


def cell(s: str, n: int = 160) -> str:
    s = " ".join(str(s).split()).replace("|", "¦")
    return s if len(s) <= n else s[: n - 1] + "…"


def main() -> None:
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    path = Path(sys.argv[1])
    try:
        log = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        sys.exit(f"shannon_report: не прочитать {path}: {e}")
    rows, n_exp = [], 0
    for run in log.get("runs") or []:
        rules = {r.get("id"): (r.get("shortDescription") or {}).get("text") or r.get("name", "")
                 for r in ((run.get("tool") or {}).get("driver") or {}).get("rules") or []}
        for res in run.get("results") or []:
            rid = res.get("ruleId", "")
            exp = exploited(res)
            n_exp += exp
            rows.append((f"{rid} {rules.get(rid, '')}".strip(), res.get("level", "warning"), place(res),
                         (res.get("message") or {}).get("text", ""), "да" if exp else "нет"))
    print("| № | Правило | Уровень | Где | Что | Взломано |")
    print("|---|---|---|---|---|---|")
    for i, (rule, level, where, what, exp) in enumerate(rows, 1):
        print(f"| S{i} | {cell(rule, 60)} | {level} | `{cell(where, 70)}` | {cell(what)} | {exp} |")
    print()
    print(f"shannon_report: находок {len(rows)}, подтверждено взломом {n_exp} — каждую подтверждённую проверить "
          "запросом на стенде, прежде чем она станет находкой аудита")


if __name__ == "__main__":
    main()
