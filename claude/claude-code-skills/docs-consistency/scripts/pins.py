#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Step 1 of docs-consistency: every `sources:` pin of the set (`info.x-sources` in OpenAPI) that is behind its source,
classed by the source's journal rows after the pin (doc-versioning → Staleness and cascade).

    python3 pins.py [<project dir>]

For each pin behind its source's `version`, one line and then the source's rows after the pin, in full:
  stale    a «ломает» row after the pin — the check stops: a P1 owned by the dependant (docs-consistency → Step 1);
  behind   only «добавляет» — not a finding: the rows are the NEW TOKENS for the checker;
  refresh  only «уточняет» — nothing; the dependant's next stamp refreshes the pin.
Each row: `<version> · <тип> · <изменение> · кого: <Кого затрагивает>`. A pin to a missing file or to a version the
source never had is doc_check.py's line, not this script's. Exit 0 — no stale pin; 1 — at least one stale.
Standard library only.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "pipeline" / "scripts"))
import where_am_i as w  # noqa: E402


def rows(doc: "w.Doc") -> list:
    """(version, type, change, affected) — the journal of a markdown document, info.x-changelog of OpenAPI."""
    if doc.rel.endswith("openapi.yaml"):
        return [(v, t, c, "") for v, t, c in doc.meta.get("rows", [])]
    m = re.search(r"^## Журнал изменений\s*\n(.*?)(?=^## |\Z)", w.read(doc.path), re.M | re.S)
    out = []
    for line in (m.group(1).splitlines() if m else []):
        cells = [c.strip() for c in re.split(r"(?<!\\)\|", line.strip().strip("|"))]
        if len(cells) >= 4 and w.VERSION_RX.search(cells[0]) and not set(cells[0]) <= set("-: "):
            out.append((cells[0], cells[3], cells[2], cells[4] if len(cells) > 4 else ""))
    return out


def main() -> None:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    docs = [d for d in w.registry(root) if d.path.is_file() and "business-requirements" not in d.rel]
    by_path = {d.rel: d for d in docs}
    counts = {"stale": 0, "behind": 0, "refresh": 0}
    total = 0
    for d in docs:
        for src in d.meta.get("sources", []):
            if "@" not in src:
                continue
            total += 1
            path, pin = src.rsplit("@", 1)
            source = by_path.get(path)
            if not source or "version" not in source.meta:
                continue
            cur = source.meta["version"]
            if w.vkey(pin) >= w.vkey(cur):
                continue
            after = [r for r in rows(source) if w.VERSION_RX.search(r[0]) and w.vkey(r[0]) > w.vkey(pin)]
            types = {r[1] for r in after}
            kind = "stale" if "ломает" in types else "behind" if "добавляет" in types else "refresh"
            counts[kind] += 1
            print(f"{kind}: {d.rel} → {path}@{pin} (сейчас {cur})")
            for v, t, c, a in after:
                print(f"    {v} · {t or '—'} · {c} · кого: {a or '—'}")
    print(f"pins: пинов {total}, устарели {counts['stale']}, отстают {counts['behind']}, "
          f"обновит штамп {counts['refresh']}")
    sys.exit(1 if counts["stale"] else 0)


if __name__ == "__main__":
    main()
