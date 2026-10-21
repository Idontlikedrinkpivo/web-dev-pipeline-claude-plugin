"""One HTML page for the iteration's progress files: documentation/plans/<version>/progress.html.

    python3 progress_page.py [<project dir>] [--version <v>]

Reads every progress file of the open iteration (the newest documentation/plans/<version>/ without summary.md, or
--version), and writes one page: a bar per stage on top, then each file in full, the most recently changed one open.
The page reloads itself every 5 seconds, so a browser tab shows the run as it goes. The Markdown files stay the
source — agents edit them; this page is only a view, rebuilt by the plugin's PostToolUse hook after each edit of a
progress file (hooks/progress-page.sh) and by hand with this command. Standard library only; silent on success.
"""
from __future__ import annotations

import datetime as dt
import html
import os
import re
import sys
from pathlib import Path

here = Path(__file__).resolve().parent
sys.path.insert(0, str(here.parent.parent / "docs-site" / "scripts"))
import mdhtml  # noqa: E402

# chain order of the stages that keep a progress file (pipeline → references/progress-files.md)
FILES = [
    ("progress-design.md", "Макеты"),
    ("progress-screen-specs.md", "ТЗ на экраны"),
    ("progress-test-cases.md", "Тест-кейсы"),
    ("progress-architecture.md", "Архитектура"),
    ("progress-scaffold.md", "Каркас"),
    ("progress.md", "Код"),
    ("progress-e2e.md", "Браузерные тесты"),
    ("test-run.md", "Проверка через интерфейс"),
    ("security-audit.md", "Аудит безопасности"),
    ("progress-deploy.md", "Релиз"),
]
STATUS = ["✅", "🔄", "🔍", "⏳", "🔁", "⛔", "⏭", "❌"]

CSS = """
:root{--bg:#fbfaf8;--card:#fff;--fg:#1f2328;--muted:#656d76;--line:#e4e2dd;--bar:#e9e6e0;--done:#2f8f5b;--acc:#3b6fd8}
@media (prefers-color-scheme:dark){:root{--bg:#16181c;--card:#1e2126;--fg:#e6e6e6;--muted:#9aa1a9;--line:#30343b;--bar:#2b2f36;--done:#3fb37a;--acc:#6e9bff}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:15px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif}
main{max-width:1180px;margin:0 auto;padding:24px 16px 64px}h1{font-size:22px;margin:0 0 4px}.sub{color:var(--muted);font-size:13px;margin-bottom:20px}
.stages{display:grid;gap:10px;margin-bottom:28px}.stage{display:grid;grid-template-columns:200px 1fr 64px;grid-template-areas:"name track pct" ". chips chips";gap:6px 12px;align-items:center;background:var(--card);border:1px solid var(--line);border-radius:10px;padding:10px 14px;text-decoration:none;color:inherit}
.stage.active{border-color:var(--acc);box-shadow:0 0 0 1px var(--acc)}.name{grid-area:name;font-weight:600}.name small{display:block;font-weight:400;color:var(--muted);font-size:12px}
.track{grid-area:track;height:10px;background:var(--bar);border-radius:6px;overflow:hidden}.fill{height:100%;background:var(--done);border-radius:6px}.pct{grid-area:pct;text-align:right;font-variant-numeric:tabular-nums;font-weight:600}
.chips{grid-area:chips;display:flex;flex-wrap:wrap;gap:6px;font-size:12px;color:var(--muted)}.chips span{background:var(--bar);border-radius:999px;padding:1px 8px}
details{background:var(--card);border:1px solid var(--line);border-radius:10px;margin:0 0 14px;padding:0 16px}summary{cursor:pointer;padding:12px 0;font-weight:600}
details>div{padding-bottom:12px;overflow-x:auto}table{border-collapse:collapse;width:100%;font-size:13.5px}th,td{border-bottom:1px solid var(--line);padding:6px 8px;text-align:left;vertical-align:top}
th{color:var(--muted);font-weight:600;white-space:nowrap}pre{background:var(--bar);padding:8px 10px;border-radius:6px;overflow-x:auto;font-size:12px}code{font-size:.92em}
details h1{font-size:18px}details h2{font-size:16px}details h3,details h4{font-size:15px}a{color:var(--acc)}.hash{display:none}.empty{color:var(--muted)}@media (max-width:640px){.stage{grid-template-columns:1fr 52px;grid-template-areas:"name pct" "track track" "chips chips"}}
"""


def open_iteration(plans: Path) -> str | None:
    vs = [p.name for p in plans.iterdir() if p.is_dir() and re.fullmatch(r"\d+(\.\d+)*", p.name)
          and not (p / "summary.md").exists()] if plans.is_dir() else []
    return max(vs, key=lambda v: [int(x) for x in v.split(".")]) if vs else None


def percent(text: str) -> int | None:
    m = re.search(r"[█░]+\s*(\d{1,3})\s*%", text)
    if m:
        return int(m.group(1))
    m = re.search(r"(\d+)\s*из\s*(\d+)", text)
    return int(int(m.group(1)) * 100 / int(m.group(2))) if m and int(m.group(2)) else None


def summary(text: str) -> tuple[str, str]:
    """The count line (first line with «из» or a colon after the bar) and the state line («обновлено …»)."""
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    count = ""
    for i, l in enumerate(lines):  # the format puts the count line right under the bar's code block
        if re.search(r"[█░]{5,}", l):
            after = [x for x in lines[i + 1:] if not x.startswith("```")]
            count = after[0] if after and not after[0].startswith("|") else ""
            break
    if not count:
        count = next((l for l in lines if re.search(r"\d+\s*из\s*\d+", l) and not l.startswith("|")
                      and len(l) < 160), "")
    state = next((l for l in reversed(lines) if "обновлено" in l.lower() and not l.startswith("|")), "")

    def short(s: str) -> str:
        s = re.sub(r"[*`]", "", s)
        return s if len(s) <= 140 else s[:137].rstrip() + "…"
    return short(count), short(state)


def main() -> None:
    args = sys.argv[1:]
    version = None
    if "--version" in args:
        i = args.index("--version"); version = args[i + 1]; del args[i:i + 2]
    root = Path(args[0] if args else os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd())
    plans = root / "documentation" / "plans"
    version = version or open_iteration(plans)
    if not version:
        return
    folder = plans / version
    found = [(f, label) for f, label in FILES if (folder / f).is_file()]
    if not found:
        return
    latest = max(found, key=lambda x: (folder / x[0]).stat().st_mtime)[0]
    stages, sections = [], []
    for f, label in found:
        text = (folder / f).read_text(encoding="utf-8", errors="replace")
        pct = percent(text)
        count, state = summary(text)
        chips = "".join(f"<span>{s} {text.count(s)}</span>" for s in STATUS if text.count(s))
        anchor = f.replace(".md", "")
        width = pct if pct is not None else 0
        stages.append(
            f'<a class="stage{" active" if f == latest else ""}" href="#{anchor}">'
            f'<div class="name">{html.escape(label)}<small>{html.escape(count or f)}</small></div>'
            f'<div class="track"><div class="fill" style="width:{width}%"></div></div>'
            f'<div class="pct">{"—" if pct is None else f"{pct}%"}</div>'
            f'<div class="chips">{chips}{f"<span>{html.escape(state)}</span>" if state else ""}</div></a>')
        body = mdhtml.convert(text).html
        sections.append(f'<details id="{anchor}"{" open" if f == latest else ""}><summary>{html.escape(label)} — '
                        f'<a href="{html.escape(f)}">{html.escape(f)}</a></summary><div>{body}</div></details>')
    now = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    page = (f'<!doctype html><html lang="ru"><head><meta charset="utf-8">'
            f'<meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<meta http-equiv="refresh" content="5"><title>Прогресс {html.escape(version)}</title>'
            f"<style>{CSS}</style></head><body><main><h1>Прогресс итерации {html.escape(version)}</h1>"
            f'<div class="sub">Страница обновляется сама каждые 5 секунд · собрана {now} из файлов прогресса '
            f"в documentation/plans/{html.escape(version)}/</div>"
            f'<div class="stages">{"".join(stages)}</div>{"".join(sections)}</main></body></html>')
    out = folder / "progress.html"
    tmp = folder / ".progress.html.tmp"
    tmp.write_text(page, encoding="utf-8")
    tmp.replace(out)  # atomic: a reload never sees half a page


if __name__ == "__main__":
    try:
        main()
    except Exception as e:  # a view must never break the run that feeds it
        print(f"progress_page: {e}", file=sys.stderr)
