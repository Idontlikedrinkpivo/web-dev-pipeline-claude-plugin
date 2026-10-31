#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Merge the two plan-review halves into plan-review.md — the deterministic part of plan-review's Report.

    python3 merge_review.py <documentation/plans/<version>/plan.md> <structural report> <judgment report> [--out <path>]

Each report is a file holding the reviewer's last message as it came back (plan-review/references/reviewer-prompt.md
→ The report): VERDICT, FINDINGS (one per line: <sev> | <units> | <lens> | <what> | <fix> | <вид правки>),
COVERAGE LEDGER, GRADE TABLE, DISMISSED, OPEN. The script writes, beside the plan unless --out names another path:

    Verdict: <verdict>                         — computed from the merged rows, never copied from either half
    checked: <sha256 of plan.md>               — the plan file as reviewed; work compares it with the plan on disk
    ## Ревью плана — <plan> — <verdict>
    the findings table                         — P0 → P3, structural rows before judgment rows within a level,
                                                 numbered once; the same units and lens from both halves is one row,
                                                 the stricter level kept
    Coverage ledger (structural half), Grade table (judgment half), Dismissed and Open (both), Not blocking (#s)

The verdict: STOP when either half returned STOP (a finding is upstream); otherwise any P0/P1 → FIX_THEN_PROCEED when
every blocking row's «Вид правки» is mechanical, else RETURN_TO_PLAN; none → PASS. A blocking row with no «Вид
правки» counts as not mechanical. Prints the verdict line, the counts and the output path.

Exit 0 — written; 1 — a file could not be read or a report has no VERDICT line. Standard library only.
"""
from __future__ import annotations

import hashlib
import re
import sys
from pathlib import Path

FIELDS = ["VERDICT", "FINDINGS", "COVERAGE LEDGER", "GRADE TABLE", "DISMISSED", "OPEN"]
FIELD = re.compile(r"^\s*(" + "|".join(FIELDS) + r")\b[ \t]*:?[ \t]*(.*)$")
SEV = re.compile(r"^P[0-3]$")
VERDICTS = ("PASS", "FIX_THEN_PROCEED", "RETURN_TO_PLAN", "STOP")
NONE = {"", "none", "нет", "—", "-", "all covered", "чисто"}


def parse(text: str) -> dict:
    """{field: [lines]} — a field's own line and the lines under it until the next field."""
    out: dict = {k: [] for k in FIELDS}
    cur = None
    for line in text.replace("```", "").splitlines():
        m = FIELD.match(line)
        if m:
            cur = m.group(1)
            if m.group(2).strip():
                out[cur].append(m.group(2).strip())
        elif cur and line.strip():
            out[cur].append(line.strip())
    return out


def findings(lines: list, half: str) -> list:
    rows = []
    for line in lines:
        cells = [c.strip() for c in line.lstrip("-•* ").split("|")]
        if len(cells) < 4 or not SEV.match(cells[0]):
            continue  # a continuation or a «none»
        sev, units, lens = cells[0], cells[1], cells[2]
        rest = cells[3:]
        kind = rest.pop() if len(rest) >= 3 else "—"
        what = rest[0] if rest else ""
        fix = " | ".join(rest[1:]) if len(rest) > 1 else ""
        rows.append({"sev": sev, "units": units, "lens": lens, "what": what, "fix": fix,
                     "kind": kind.strip("` ") or "—", "half": half})
    return rows


def unit_key(units: str) -> tuple:
    ids = sorted(set(re.findall(r"U\d+", units)))
    return tuple(ids) if ids else (units.strip().lower(),)


def merge(rows: list) -> list:
    """One row per (units, lens); the stricter level wins, its text kept."""
    best: dict = {}
    for r in rows:
        key = (unit_key(r["units"]), r["lens"].strip().lower())
        if key not in best or r["sev"] < best[key]["sev"]:
            best[key] = r
    order = {"structural": 0, "judgment": 1}
    return sorted(best.values(), key=lambda r: (r["sev"], order[r["half"]]))


def cell(text: str) -> str:
    return text.replace("|", "\\|").strip() or "—"


def body(lines: list, fallback: str) -> str:
    text = "; ".join(lines).strip()
    return fallback if text.lower().strip(".") in NONE else text


def main() -> int:
    args = sys.argv[1:]
    if len(args) < 3 or args[0] in ("-h", "--help"):
        print(__doc__)
        return 1
    plan, s_path, j_path = Path(args[0]), Path(args[1]), Path(args[2])
    out = Path(args[args.index("--out") + 1]) if "--out" in args and args.index("--out") + 1 < len(args) \
        else plan.parent / "plan-review.md"
    try:
        digest = hashlib.sha256(plan.read_bytes()).hexdigest()
        s, j = (parse(p.read_text(encoding="utf-8")) for p in (s_path, j_path))
    except OSError as e:
        print(f"merge_review: {e}")
        return 1
    halves = {"structural": s, "judgment": j}
    verdicts = {}
    for name, rep in halves.items():
        v = next((w for w in VERDICTS if rep["VERDICT"] and w in rep["VERDICT"][0].upper()), "")
        if not v:
            print(f"merge_review: the {name} report has no VERDICT line ({VERDICTS})")
            return 1
        verdicts[name] = v

    posix = plan.as_posix()
    shown = posix[posix.index("documentation/"):] if "documentation/" in posix else posix  # repo-relative
    rows = merge(findings(s["FINDINGS"], "structural") + findings(j["FINDINGS"], "judgment"))
    blocking = [r for r in rows if r["sev"] in ("P0", "P1")]
    if "STOP" in verdicts.values():
        verdict = "STOP"
    elif blocking:
        verdict = "FIX_THEN_PROCEED" if all(r["kind"].lower() == "mechanical" for r in blocking) else "RETURN_TO_PLAN"
    else:
        verdict = "PASS"

    table = ["| # | Важность | Юниты | Аспект | Находка | Исправление | Вид правки |", "|---|---|---|---|---|---|---|"]
    for i, r in enumerate(rows, 1):
        kind = r["kind"] if r["sev"] in ("P0", "P1") else "—"
        table.append(f"| {i} | {r['sev']} | {cell(r['units'])} | {cell(r['lens'])} | {cell(r['what'])} | "
                     f"{cell(r['fix'])} | {cell(kind)} |")
    not_blocking = [f"#{i}" for i, r in enumerate(rows, 1) if r["sev"] in ("P2", "P3")]
    dismissed = [x for x in (body(s["DISMISSED"], ""), body(j["DISMISSED"], "")) if x]
    open_ = [x for x in (body(s["OPEN"], ""), body(j["OPEN"], "")) if x]
    text = "\n".join([
        f"Verdict: {verdict}",
        f"checked: {digest}",
        "",
        f"## Ревью плана — {shown} — {verdict}",
        "",
        *table,
        "",
        f"**Coverage ledger** — {body(s['COVERAGE LEDGER'], 'все строки реестра покрыты.')}",
        f"**Grade table** — {body(j['GRADE TABLE'], 'расхождений с каскадом нет.')}",
        f"**Dismissed** — {' '.join(dismissed) or 'нет.'}",
        f"**Not blocking** — {', '.join(not_blocking) or 'нет.'}",
        f"**Open** — {' '.join(open_) or 'нет.'}",
        "",
    ])
    out.write_text(text, encoding="utf-8")
    counts = {lv: sum(r["sev"] == lv for r in rows) for lv in ("P0", "P1", "P2", "P3")}
    print(f"Verdict: {verdict} · halves {verdicts['structural']} / {verdicts['judgment']} · "
          + " ".join(f"{k}:{v}" for k, v in counts.items()) + f" · {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
