"""An HTML page beside each progress file: progress-design.md -> progress-design.html, progress.md ->
progress.html, test-run.md -> test-run.html, and so on.

    python3 progress_page.py <progress file.md>            # one page
    python3 progress_page.py [<project dir>] [--version <v>]  # every progress file of the iteration

The page shows the file's bar as a real progress bar, its count and state lines and status counts, then the file
in full; it reloads itself every 5 seconds, so a browser tab follows the run. The Markdown file stays the source —
agents edit it; the page is only its view, rebuilt by the plugin's PostToolUse hook after each edit of a progress
file (hooks/progress-page.sh) and by hand with this command. Standard library only; silent on success.
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

# the files the stages keep (pipeline → references/progress-files.md), with the stage's name
FILES = {
    "progress-design.md": "Макеты", "progress-screen-specs.md": "ТЗ на экраны",
    "progress-test-cases.md": "Тест-кейсы", "progress-architecture.md": "Архитектура",
    "progress-scaffold.md": "Каркас", "progress.md": "Код",
    "test-run.md": "Проверка через интерфейс", "security-audit.md": "Аудит безопасности",
    "progress-deploy.md": "Релиз", "progress-mutation.md": "Мутации",
}
STATUS = ["✅", "❌", "🔄", "🔍", "⏳", "🔁", "⛔", "⏭", "🖼", "❓"]


def status_counts(lines: list[str], lo: int = 0, hi: int | None = None) -> list[tuple[str, int]]:
    """One count per row of the first table with a «Статус» column in lines[lo:hi], by the status's words before
    any colon («✅ прошёл», «❌ не прошёл», «⏭ не автоматизирован»). Never the emoji counted over the whole file:
    a case is named again in another run's table and in the lists under the verdict."""
    hi = len(lines) if hi is None else hi
    i = lo
    while i < hi:
        if lines[i].lstrip().startswith("|") and i + 1 < hi and re.match(r"^\s*\|[\s:|-]+\|\s*$", lines[i + 1]):
            head = [c.strip() for c in lines[i].strip().strip("|").split("|")]
            col = next((k for k, c in enumerate(head) if c.startswith("Статус")), None)
            j = i + 2
            rows = []
            while j < hi and lines[j].lstrip().startswith("|"):
                rows.append([c.strip() for c in lines[j].strip().strip("|").split("|")])
                j += 1
            if col is not None:
                counts: dict[str, int] = {}
                for r in rows:
                    cell = r[col] if col < len(r) else ""
                    if cell[:1] and not cell[:1].isalnum():
                        label = cell.split(":")[0].strip()
                        counts[label] = counts.get(label, 0) + 1
                order = {e: n for n, e in enumerate(STATUS)}
                return sorted(counts.items(), key=lambda kv: (order.get(kv[0][:1], len(STATUS)), -kv[1]))
            i = j
            continue
        i += 1
    return []


# the files whose bar the page computes from the rows' statuses — agents change rows and forgot the bar (it stayed at
# 0% through whole stages: architecture, screen specs, test cases); a row in progress counts in part, so the bar
# moves with every status, not only when a document is finished
DERIVED = {"progress-design.md", "progress-screen-specs.md", "progress-test-cases.md", "progress-architecture.md",
           "security-audit.md", "progress-scaffold.md", "progress-deploy.md"}
WEIGHT = {"✅": 1.0, "⏭": 1.0, "🔍": 2 / 3, "🔄": 1 / 3, "🔁": 1 / 3, "⏳": 0.0, "⛔": 0.0}


def derived(text: str) -> tuple[int, str] | None:
    """(percent, count line) from the statuses of the main table — the first table with «Статус» under the file's
    first bar: ✅ and ⏭ whole, 🔍 two thirds, 🔄 and 🔁 a third, ⏳ and ⛔ nothing."""
    lines = text.splitlines()
    start = next((i for i, l in enumerate(lines) if re.search(r"[█░]{5,}", l)), 0)
    heads = [i for i, l in enumerate(lines) if re.match(r"^#{1,4}\s", l) and i > start]
    end = heads[0] if heads else len(lines)
    for i in range(start, end - 1):
        if lines[i].lstrip().startswith("|") and re.match(r"^\s*\|[\s:|-]+\|\s*$", lines[i + 1]):
            head = [c.strip() for c in lines[i].strip().strip("|").split("|")]
            col = next((k for k, c in enumerate(head) if c.startswith("Статус")), None)
            if col is None:
                continue
            marks = []
            for row in lines[i + 2:end]:
                if not row.lstrip().startswith("|"):
                    break
                cells = [c.strip() for c in row.strip().strip("|").split("|")]
                cell = cells[col] if col < len(cells) else ""
                if cell[:1] in WEIGHT:
                    marks.append(cell[:1])
            if not marks:
                return None
            pct = int(sum(WEIGHT[m] for m in marks) * 100 // len(marks))
            done = sum(1 for m in marks if m in "✅⏭")
            extra = [f"{w} {n}" for w, n in (("в работе", sum(1 for m in marks if m in "🔄🔁")),
                                              ("на проверке", marks.count("🔍")), ("остановлено", marks.count("⛔")))
                     if n]
            return pct, f"Готово: {done} из {len(marks)}" + (" · " + " · ".join(extra) if extra else "")
    return None


def bars(text: str) -> list[dict]:
    """Every bar of the file, in order: the heading it sits under (none above the first `## ` — the file's own
    bar), its percent, its count line, and the status counts of its own section's table."""
    lines = text.splitlines()
    heads = [(i, len(m.group(1)), re.sub(r"[*`]", "", m.group(2)).strip())
             for i, l in enumerate(lines) for m in [re.match(r"^(#{1,4})\s+(.*)$", l)] if m]
    out = []
    for i, l in enumerate(lines):
        m = re.match(r"^\s*[█░]{5,}\s*(\d{1,3})\s*%", l)
        if not m:
            continue
        above = [h for h in heads if h[0] < i and h[1] >= 2]
        label = above[-1][2] if above else ""
        nxt = next((h[0] for h in heads if h[0] > i), len(lines))
        count = ""
        for x in lines[i + 1:nxt]:
            x = x.strip()
            if x and not x.startswith(("```", "|", "#")):
                count = re.sub(r"[*`]", "", x)
                break
        out.append({"label": label, "pct": int(m.group(1)), "count": count,
                    "chips": status_counts(lines, i, nxt)})
    return out


CSS = """
:root{--bg:#fbfaf8;--card:#fff;--fg:#1f2328;--muted:#656d76;--line:#e4e2dd;--bar:#e9e6e0;--done:#2f8f5b;--acc:#3b6fd8}
@media (prefers-color-scheme:dark){:root{--bg:#16181c;--card:#1e2126;--fg:#e6e6e6;--muted:#9aa1a9;--line:#30343b;--bar:#2b2f36;--done:#3fb37a;--acc:#6e9bff}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:15px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif}
main{max-width:1180px;margin:0 auto;padding:24px 16px 64px}.stage{font-size:13px;color:var(--muted);text-transform:uppercase;letter-spacing:.04em}
h1{font-size:24px;line-height:1.25;margin:4px 0 16px}.head{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:16px 18px;margin-bottom:24px}
.head>.lbl{font-size:13px;font-weight:600;color:var(--muted);margin-bottom:2px}.row{display:flex;align-items:baseline;justify-content:space-between;gap:12px}.count{font-weight:600}.pct{font-size:28px;font-weight:700;font-variant-numeric:tabular-nums}
.track{height:12px;background:var(--bar);border-radius:7px;overflow:hidden;margin:10px 0}.fill{height:100%;background:var(--done);border-radius:7px}
.chips{display:flex;flex-wrap:wrap;gap:6px;font-size:13px;color:var(--muted)}.chips span{background:var(--bar);border-radius:999px;padding:2px 10px}
.sub{color:var(--muted);font-size:12.5px;margin-top:10px}.runs{margin-top:14px;border-top:1px solid var(--line);padding-top:10px;display:grid;gap:10px}
.run .lbl{font-size:13px;font-weight:600}.run .cnt{font-size:13px;color:var(--muted)}.run .track{height:8px;margin:5px 0}.run .chips{font-size:12px}.body{overflow-x:auto}.body h1{display:none}.body h2{font-size:18px;margin:28px 0 10px}.body h3{font-size:16px}
table{border-collapse:collapse;width:100%;font-size:14px;background:var(--card)}th,td{border-bottom:1px solid var(--line);padding:7px 9px;text-align:left;vertical-align:top}
th{color:var(--muted);font-weight:600;white-space:nowrap}pre{background:var(--bar);padding:8px 10px;border-radius:6px;overflow-x:auto;font-size:12px}code{font-size:.92em}
a{color:var(--acc)}.hash{display:none}
.bar2{display:flex;align-items:center;gap:10px;font-weight:600;font-variant-numeric:tabular-nums}.bar2 .track{flex:1}
td:first-child{white-space:nowrap}
"""


def percent(text: str) -> int | None:
    m = re.search(r"[█░]+\s*(\d{1,3})\s*%", text)
    if m:
        return int(m.group(1))
    m = re.search(r"(\d+)\s*из\s*(\d+)", text)
    return int(int(m.group(1)) * 100 / int(m.group(2))) if m and int(m.group(2)) else None


def lines_of(text: str) -> tuple[str, str]:
    """The count line (right under the bar's block) and the state line («… обновлено …»)."""
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    count = ""
    for i, l in enumerate(lines):
        if re.search(r"[█░]{5,}", l):
            after = [x for x in lines[i + 1:] if not x.startswith("```")]
            count = after[0] if after and not after[0].startswith(("|", "#")) else ""
            break
    if not count:
        count = next((l for l in lines if re.search(r"\d+\s*из\s*\d+", l) and not l.startswith("|") and len(l) < 160), "")
    state = next((l for l in reversed(lines) if "обновлено" in l.lower() and not l.startswith("|")), "")

    def clean(s: str) -> str:
        return re.sub(r"[*`]", "", s)
    return clean(count), clean(state)


def page(md: Path) -> None:
    text = md.read_text(encoding="utf-8", errors="replace")
    pct = percent(text)
    count, state = lines_of(text)
    computed = derived(text) if md.name in DERIVED else None
    if computed:
        pct, count = computed
    title = next((re.sub(r"[*`]", "", l[2:]).strip() for l in text.splitlines() if l.startswith("# ")), md.stem)
    found = bars(text)
    chip = lambda cs: "".join(f"<span>{html.escape(label)}: {n}</span>" for label, n in cs)
    chips = chip(found[0]["chips"]) if found else ""
    runs = "".join(
        f'<div class="run"><div class="row"><div class="lbl">{html.escape(b["label"] or "—")}</div>'
        f'<div class="lbl">{b["pct"]}%</div></div><div class="cnt">{html.escape(b["count"])}</div>'
        f'<div class="track"><div class="fill" style="width:{b["pct"]}%"></div></div>'
        f'<div class="chips">{chip(b["chips"])}</div></div>' for b in found[1:])
    lead = (found[0]["label"] or "Общий итог") if len(found) > 1 else ""
    # the bar and the count line are drawn in the header, not repeated in the body
    body_md = re.sub(r"```text\n[█░\s\d%]+\n```\n*", "", text, count=1)
    if count:
        body_md = body_md.replace(count, "", 1) if count in body_md else body_md
    body = mdhtml.convert(body_md).html
    # a section's own bar (a re-run, pass 2, the fixes after the final review) is drawn as a bar too
    body = re.sub(r'<pre><code class="language-text">[█░\s]+?(\d{1,3})\s*%\s*</code></pre>',
                  lambda m: f'<div class="bar2"><div class="track"><div class="fill" style="width:{m.group(1)}%">'
                            f'</div></div><span>{m.group(1)}%</span></div>', body)
    now = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    width = pct if pct is not None else 0
    doc = (f'<!doctype html><html lang="ru"><head><meta charset="utf-8">'
           f'<meta name="viewport" content="width=device-width,initial-scale=1">'
           f'<meta http-equiv="refresh" content="5"><title>{html.escape(title)}</title><style>{CSS}</style></head>'
           f'<body><main><div class="stage">{html.escape(FILES.get(md.name, md.stem))}</div>'
           f"<h1>{html.escape(title)}</h1>"
           f'<div class="head">{f"<div class=lbl>{html.escape(lead)}</div>" if lead else ""}'
           f'<div class="row"><div class="count">{html.escape(count)}</div>'
           f'<div class="pct">{"—" if pct is None else f"{pct}%"}</div></div>'
           f'<div class="track"><div class="fill" style="width:{width}%"></div></div>'
           f'<div class="chips">{chips}</div>'
           f'{f"<div class=runs>{runs}</div>" if runs else ""}'
           f'<div class="sub">{html.escape(state)}{" · " if state else ""}страница обновляется сама каждые 5 секунд · '
           f'собрана {now} из <a href="{html.escape(md.name)}">{html.escape(md.name)}</a></div></div>'
           f'<div class="body">{body}</div></main></body></html>')
    out = md.with_suffix(".html")
    tmp = md.with_name("." + out.name + ".tmp")
    tmp.write_text(doc, encoding="utf-8")
    tmp.replace(out)  # atomic: a reload never sees half a page


def open_iteration(plans: Path) -> str | None:
    vs = [p.name for p in plans.iterdir() if p.is_dir() and re.fullmatch(r"\d+(\.\d+)*", p.name)
          and not (p / "summary.md").exists()] if plans.is_dir() else []
    return max(vs, key=lambda v: [int(x) for x in v.split(".")]) if vs else None


def main() -> None:
    args = sys.argv[1:]
    if args and args[0].endswith(".md"):
        md = Path(args[0])
        if md.name in FILES and md.is_file():
            page(md)
        return
    version = None
    if "--version" in args:
        i = args.index("--version"); version = args[i + 1]; del args[i:i + 2]
    root = Path(args[0] if args else os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd())
    plans = root / "documentation" / "plans"
    version = version or open_iteration(plans)
    if not version:
        return
    for name in FILES:
        if (plans / version / name).is_file():
            page(plans / version / name)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:  # a view must never break the run that feeds it
        print(f"progress_page: {e}", file=sys.stderr)
