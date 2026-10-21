"""Build a static documentation site from documentation/ (standard library only; Node only for the API page).

    python3 build_site.py [--docs documentation] [--out documentation/site] [--title "…"] [--no-api]

Every Markdown document becomes a page with the site's navigation, search and cross-links: an id like FR-12,
UC-4, BR-3, NFR-6, TC-27, S-3, З-2 links to the row, heading or screen-spec file that defines it, and an
operationId in backticks links to the API page. Diagrams (.svg) are copied beside their pages. The API page is
built by Redocly (npx) from documentation/api/openapi.yaml, or, without Node, as a table of operations.
documentation/plans/ (working files) is never included. Prints a short report: pages, ids, ids mentioned but never defined,
broken links. The site opens from disk (index.html) — no server needed. It lives in documentation/site/ and is
committed, so a clone has it without a build: the pages carry the commit and date of the documents' last change,
not the build time, and the navigation sits in assets/nav.js, so a rebuild over unchanged documents changes
nothing and an edited document changes its own page, not every page.
"""
from __future__ import annotations

import datetime as dt
import html
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import mdhtml  # noqa: E402

SECTIONS = [
    ("requirements", "Требования"), ("db", "Данные"), ("api", "API"), ("architecture", "Архитектура"),
    ("ui", "Интерфейс"), ("deploy", "Развёртывание"), ("operations", "Эксплуатация"), ("project-map", "Карта проекта"),
]
ID = r"(?:FR|NFR|BR|UC|AC|TC|R|S|M)-\d+(?:\.\d+)*|[ЗП]-\d+"
ID_RE = re.compile(rf"(?<![\w\-/#.])({ID})(?![\w\-])")
KINDS = ["FR", "NFR", "BR", "UC", "TC", "S", "З"]
KIND_LABEL = {"FR": "функциональных требований", "NFR": "нефункциональных требований", "BR": "бизнес-правил",
              "UC": "сценариев", "TC": "тест-кейсов", "S": "экранов", "З": "запросов эксплуатации"}

ASSET_EXT = {".svg", ".png", ".jpg", ".jpeg", ".gif", ".webp"}


def args() -> dict:
    a = sys.argv[1:]
    opt = {"docs": "documentation", "out": None, "title": None, "api": True}
    i = 0
    while i < len(a):
        k = a[i]
        if k == "--no-api":
            opt["api"] = False
            i += 1
            continue
        opt[k.lstrip("-")] = a[i + 1]
        i += 2
    return opt


def rel(target: str, frm: str) -> str:
    """Relative URL from page `frm` (site path) to site path `target`."""
    return os.path.relpath(target, os.path.dirname(frm) or ".").replace(os.sep, "/")


class Site:
    def __init__(self, docs: Path, out: Path, title: str | None, api: bool):
        self.docs, self.out, self.api_on = docs, out, api
        self.title = title or self.project_name()
        self.pages: list[dict] = []          # {src, url, section, title, text}
        self.defs: dict[str, str] = {}       # id -> url#anchor (or url)
        self.ops: dict[str, str] = {}        # operationId -> "METHOD /path · summary"
        self.mentioned: dict[str, int] = {}
        self.broken: list[str] = []
        self.api_mode = "нет"
        self.out_name = out.resolve().relative_to(docs.resolve()).parts[0] \
            if str(out.resolve()).startswith(str(docs.resolve()) + os.sep) else None

    def project_name(self) -> str:
        readme = self.docs.parent / "README.md"
        if readme.exists():
            m = re.search(r"^#\s+(.+)$", readme.read_text(encoding="utf-8", errors="replace"), re.M)
            if m:
                return re.sub(r"[`*]", "", m.group(1)).split(" — ")[0].strip()
        return self.docs.resolve().parent.name

    # ---------- collect ----------
    def collect(self) -> None:
        order = {name: i for i, (name, _) in enumerate(SECTIONS)}
        files = []
        for p in sorted(self.docs.rglob("*.md")):
            r = p.relative_to(self.docs)
            top = r.parts[0] if len(r.parts) > 1 else ""
            if top in ("plans", self.out_name) or p.name.startswith("progress"):
                continue
            natural = [int(x) if x.isdigit() else x for x in re.split(r"(\d+)", str(r))]  # S-2 before S-11
            files.append((order.get(top, len(SECTIONS)), natural, str(r), p, top))
        for _, _, r, p, top in sorted(files, key=lambda f: (f[0], [(0, x) if isinstance(x, int) else (1, x) for x in f[1]])):
            text = p.read_text(encoding="utf-8", errors="replace")
            meta, body = mdhtml.split_frontmatter(text)
            m = re.search(r"^#\s+(.+)$", body, re.M)
            title = re.sub(r"[`*]", "", m.group(1)).strip() if m else meta.get("title") or p.stem
            self.pages.append({"src": p, "rel": r, "url": r[:-3] + ".html", "section": top, "title": title,
                               "text": text, "meta": meta})

    def short_titles(self) -> None:
        """Menu titles: drop the tail a section's pages share («… — Реестр ИИ инициатив, SRS»), keep the rest
        («Заявка — подача»); a title that would still repeat in its section stays whole."""
        from collections import Counter
        by_section: dict = {}
        for pg in self.pages:
            by_section.setdefault(pg["section"], []).append(pg)
        for pages in by_section.values():
            tails = Counter(pg["title"].split(" — ")[-1] for pg in pages if " — " in pg["title"])
            common = {tail for tail, n in tails.items() if n >= 2}
            for pg in pages:
                parts = pg["title"].split(" — ")
                pg["short"] = " — ".join(parts[:-1]) if len(parts) > 1 and parts[-1] in common else pg["title"]
            seen = Counter(pg["short"] for pg in pages)
            for pg in pages:
                if seen[pg["short"]] > 1:
                    pg["short"] = pg["title"]

    def index_ids(self) -> None:
        for pg in self.pages:  # a screen-spec file names its screen: S-3-card.md defines S-3
            m = re.match(r"^(S-\d+)-", pg["src"].name)
            if m:
                self.defs[m.group(1)] = pg["url"]
        for pg in self.pages:
            for line in pg["text"].splitlines():
                m = re.match(rf"^\|\s*[*`]*({ID})[*`]*\s*\|", line) or re.match(rf"^#{{1,6}}\s+[*`]*({ID})\b", line) or re.match(rf"^\*\*({ID})\.", line)
                if m and m.group(1) not in self.defs:
                    self.defs[m.group(1)] = f"{pg['url']}#{m.group(1)}"

    def index_ops(self) -> None:
        api = self.docs / "api"
        if not (api / "openapi.yaml").exists():
            return
        root = (api / "openapi.yaml").read_text(encoding="utf-8", errors="replace")
        blocks = []  # (path, text of its operations)
        in_paths, cur = False, None
        for line in root.splitlines():
            if re.match(r"^paths:\s*$", line):
                in_paths = True
                continue
            if in_paths and re.match(r"^\S", line):
                in_paths = False
            if in_paths:
                m = re.match(r"^  (['\"]?/[^:'\"]*['\"]?):\s*$", line)
                if m:
                    cur = m.group(1).strip("'\"")
                    blocks.append([cur, ""])
                    continue
                ref = re.match(r"^\s+\$ref:\s*['\"]?([^'\"#\s]+)", line)
                if ref and cur and (api / ref.group(1)).exists():
                    blocks[-1][1] += (api / ref.group(1)).read_text(encoding="utf-8", errors="replace")
                elif cur:
                    blocks[-1][1] += line + "\n"
        for path, text in blocks:
            method = None
            for line in text.splitlines():
                m = re.match(r"^\s{0,4}(get|post|put|patch|delete|head|options):\s*$", line)
                if m:
                    method = m.group(1).upper()
                op = re.match(r"^\s+operationId:\s*['\"]?(\w+)", line)
                if op and method:
                    summ = re.search(rf"operationId:\s*['\"]?{op.group(1)}['\"]?\s*\n(?:.*\n){{0,6}}?\s+summary:\s*(.+)", text)
                    if not summ:
                        summ = re.search(rf"{method.lower()}:\s*\n(?:.*\n){{0,6}}?\s+summary:\s*(.+)", text)
                    self.ops[op.group(1)] = f"{method} {path}" + (f" · {summ.group(1).strip()}" if summ else "")

    # ---------- render ----------
    def hooks(self, pg: dict) -> mdhtml.Hooks:
        url = pg["url"]
        anchors_here = {i for i, d in self.defs.items() if d == f"{url}#{i}"}
        placed: set = set()

        def link(href: str) -> str:
            if re.match(r"^[a-z]+:", href) or href.startswith("#"):
                return href
            path, _, frag = href.partition("#")
            target = os.path.normpath(os.path.join(os.path.dirname(pg["rel"]), path)).replace(os.sep, "/")
            if path.endswith(".md"):
                site_target = target[:-3] + ".html"
                if not any(p["url"] == site_target for p in self.pages):
                    self.broken.append(f"{pg['rel']} → {href}")
                    return href
                return rel(site_target, url) + (f"#{frag}" if frag else "")
            return href

        def autolink(text: str) -> str:
            def one(m: re.Match) -> str:
                i = m.group(1)
                d = self.defs.get(i)
                local = i[0] in "ЗП"  # query and procedure ids live inside the operations document only
                if local and (not d or not d.startswith(url + "#")):
                    return i
                self.mentioned[i] = self.mentioned.get(i, 0) + 1
                if not d:
                    return i
                page, _, frag = d.partition("#")
                href = (rel(page, url) if page != url else "") + (f"#{frag}" if frag else "")
                return f'<a class="ref" href="{html.escape(href or "#")}">{i}</a>'
            return ID_RE.sub(one, text)

        def anchor(text: str) -> str | None:
            t = re.sub(r"[*`]", "", text).strip()
            m = re.match(rf"^({ID})\b", t)
            if m and m.group(1) in anchors_here and m.group(1) not in placed:
                placed.add(m.group(1))
                return m.group(1)
            return None

        def code_link(code: str) -> str | None:
            if code in self.ops and self.api_mode != "нет":
                return rel("api/index.html", url) + f"#operation/{code}"
            if code.endswith(".md") and " " not in code:
                r = code[len("documentation/"):] if code.startswith("documentation/") else \
                    os.path.normpath(os.path.join(os.path.dirname(pg["rel"]), code)).replace(os.sep, "/")
                if any(p["rel"] == r for p in self.pages):
                    return rel(r[:-3] + ".html", url)
            return None

        return mdhtml.Hooks(link=link, autolink=autolink, anchor=anchor, code_link=code_link)

    def nav_data(self) -> list:
        """[{label, items: [[url, title], …]}] for assets/nav.js; site.js draws it and marks the current page."""
        out = []
        labels = dict(SECTIONS)
        for name, label in SECTIONS + [("", "Прочее")]:
            pages = [p for p in self.pages if (p["section"] or "") == name or (name == "" and p["section"] not in labels)]
            items = [["api/index.html", "Контракт API"]] if name == "api" and self.api_mode != "нет" else []
            items += [[p["url"], p.get("short", p["title"])] for p in pages]
            if items:
                out.append({"label": label, "items": items})
        return out

    def nav(self, current: str) -> str:
        out = []
        labels = dict(SECTIONS)
        for name, label in SECTIONS + [("", "Прочее")]:
            pages = [p for p in self.pages if (p["section"] or "") == name or
                     (name == "" and p["section"] not in labels)]
            items = []
            if name == "api" and self.api_mode != "нет":
                items.append(("api/index.html", "Контракт API"))
            items += [(p["url"], p.get("short", p["title"])) for p in pages]
            if not items:
                continue
            links = "".join(f'<a href="{html.escape(rel(u, current))}"{" class=cur" if u == current else ""}>'
                            f"{html.escape(t)}</a>" for u, t in items)
            opened = any(u == current for u, _ in items)
            out.append(f'<details{" open" if opened else ""}><summary>{label}</summary>{links}</details>')
        return "".join(out)

    def page(self, url: str, title: str, body: str, toc: list, meta: dict) -> str:
        root = "/".join([".."] * url.count("/")) or "."
        info = " · ".join(f"{k} {html.escape(meta[k])}" for k in ("version", "updated", "reviewed") if meta.get(k))
        toc_html = "".join(f'<a class="l{lv}" href="#{s}">{html.escape(t)}</a>' for lv, t, s in toc if 2 <= lv <= 3)
        return f"""<!doctype html><html lang="ru"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(title)} — {html.escape(self.title)}</title>
<link rel="stylesheet" href="{root}/assets/site.css"></head><body>
<header><button class="menu" aria-label="Меню" onclick="document.body.classList.toggle('nav-open')">☰</button>
<a class="brand" href="{root}/index.html">{html.escape(self.title)}</a>
<div class="search"><input id="q" type="search" placeholder="Поиск: текст или номер, например FR-12" autocomplete="off">
<div id="results"></div></div></header>
<div class="wrap"><nav id="nav"></nav><main>
{f'<div class="meta">{info}</div>' if info else ''}{body}</main>
<aside>{f'<div class="toc"><b>На странице</b>{toc_html}</div>' if toc_html else ''}</aside></div>
<footer id="foot"></footer>
<script>window.SITE_ROOT="{root}";window.PAGE="{url}";</script><script src="{root}/assets/nav.js"></script>
<script src="{root}/assets/search-index.js"></script>
<script src="{root}/assets/site.js"></script></body></html>"""

    def commit(self) -> str:
        """The commit and date of the documents' last change (the site folder left out), so the pages stay
        byte-identical while the documents do not change."""
        if hasattr(self, "_commit"):
            return self._commit
        spec = ["--", "."] + ([f":(exclude){self.out_name}"] if self.out_name else [])
        try:
            r = subprocess.run(["git", "-C", str(self.docs), "log", "-1", "--format=%cs · коммит %h"] + spec,
                               capture_output=True, text=True, timeout=10).stdout.strip()
        except Exception:
            r = ""
        self._commit = r or "незакоммиченные изменения"
        return self._commit

    def build_api(self) -> None:
        spec = self.docs / "api" / "openapi.yaml"
        if not spec.exists() or not self.api_on:
            return
        target = self.out / "api" / "index.html"
        target.parent.mkdir(parents=True, exist_ok=True)
        try:
            r = subprocess.run(["npx", "--yes", "@redocly/cli@latest", "build-docs", str(spec), "--output", str(target)],
                               capture_output=True, text=True, timeout=300)
            if r.returncode == 0 and target.exists():
                back = ('<a href="../index.html" style="position:fixed;right:16px;bottom:16px;z-index:100;'
                        'background:#2f5fd0;color:#fff;padding:8px 14px;border-radius:8px;text-decoration:none;'
                        'font:14px sans-serif">← К документации</a>')
                page = target.read_text(encoding="utf-8")
                target.write_text(page.replace("<body>", "<body>" + back, 1), encoding="utf-8")
                self.api_mode = "Redoc"
                return
        except Exception:
            pass
        rows = "".join(f'<tr id="operation/{html.escape(o)}"><td><code>{html.escape(o)}</code></td>'
                       f"<td>{html.escape(d)}</td></tr>" for o, d in sorted(self.ops.items(), key=lambda x: x[1]))
        body = (f"<h1>Контракт API</h1><p>Полный контракт — <code>documentation/api/openapi.yaml</code>. "
                f"Здесь — список операций (Node.js не найден, интерактивная страница не собрана).</p>"
                f'<div class="table"><table><thead><tr><th>operationId</th><th>Операция</th></tr></thead>'
                f"<tbody>{rows}</tbody></table></div>")
        target.write_text(self.page("api/index.html", "Контракт API", body, [], {}), encoding="utf-8")
        self.api_mode = "таблица операций"

    def build(self) -> None:
        if self.out.exists():
            shutil.rmtree(self.out)
        (self.out / "assets").mkdir(parents=True)
        self.collect()
        self.short_titles()
        self.index_ids()
        self.index_ops()
        self.build_api()
        search = []
        for pg in self.pages:
            res = mdhtml.convert(pg["text"], self.hooks(pg))
            target = self.out / pg["url"]
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(self.page(pg["url"], pg["title"], res.html, res.headings, res.meta), encoding="utf-8")
            plain = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", res.html))
            search.append({"t": pg["title"], "u": pg["url"], "s": dict(SECTIONS).get(pg["section"], ""),
                           "x": html.unescape(plain)[:6000]})
        for p in self.docs.rglob("*"):
            r = p.relative_to(self.docs)
            if p.suffix.lower() in ASSET_EXT and r.parts[0] not in ("plans", self.out_name):
                (self.out / r).parent.mkdir(parents=True, exist_ok=True)
                shutil.copy(p, self.out / r)
        here = Path(__file__).resolve().parent.parent / "assets"
        shutil.copy(here / "site.css", self.out / "assets" / "site.css")
        shutil.copy(here / "site.js", self.out / "assets" / "site.js")
        ids = {i: d for i, d in self.defs.items()}
        (self.out / "assets" / "nav.js").write_text(
            "window.NAV=" + json.dumps(self.nav_data(), ensure_ascii=False) + ";window.FOOT="
            + json.dumps("Документация на " + self.commit(), ensure_ascii=False) + ";", encoding="utf-8")
        (self.out / "assets" / "search-index.js").write_text(
            "window.DOCS=" + json.dumps(search, ensure_ascii=False) + ";window.IDS=" + json.dumps(ids, ensure_ascii=False) + ";",
            encoding="utf-8")
        self.home()
        self.report()

    def home(self) -> None:
        counts = []
        for k in KINDS:
            n = sum(1 for i in self.defs if i.split("-")[0] == k)
            if n:
                counts.append(f"<div><b>{n}</b><span>{KIND_LABEL[k]}</span></div>")
        cards = []
        labels = dict(SECTIONS)
        for name, label in SECTIONS:
            pages = [p for p in self.pages if p["section"] == name]
            if name == "api" and self.api_mode != "нет":
                pages = [{"url": "api/index.html", "title": "Контракт API"}] + pages
            if pages:
                links = "".join(f'<a href="{html.escape(p["url"])}">{html.escape(p.get("short", p["title"]))}</a>'
                                for p in pages[:12])
                more = f'<span class="more">и ещё {len(pages) - 12}</span>' if len(pages) > 12 else ""
                cards.append(f'<section class="card"><h2>{label}</h2>{links}{more}</section>')
        other = [p for p in self.pages if p["section"] not in labels]
        if other:
            cards.append('<section class="card"><h2>Прочее</h2>' + "".join(
                f'<a href="{html.escape(p["url"])}">{html.escape(p["title"])}</a>' for p in other) + "</section>")
        body = (f'<h1>{html.escape(self.title)}</h1><p class="lead">Документация проекта: требования, данные, API, '
                f'архитектура, интерфейс и эксплуатация. Номера требований, сценариев, тест-кейсов и экранов — '
                f'ссылки на их определение; поиск — вверху страницы.</p>'
                f'<div class="counts">{"".join(counts)}</div><div class="cards">{"".join(cards)}</div>')
        (self.out / "index.html").write_text(self.page("index.html", "Обзор", body, [], {}), encoding="utf-8")

    def report(self) -> None:
        missing = sorted((i for i in self.mentioned if i not in self.defs), key=lambda i: -self.mentioned[i])
        kinds = ", ".join(f"{k} {sum(1 for i in self.defs if i.split('-')[0] == k)}" for k in KINDS
                          if any(i.split('-')[0] == k for i in self.defs))
        print(f"site: {self.out}/index.html")
        print(f"pages: {len(self.pages)} · API: {self.api_mode} · ids defined: {kinds or 'none'}")
        if missing:
            print(f"ids mentioned but not defined ({len(missing)}): {', '.join(missing[:20])}")
        if self.broken:
            print(f"broken links ({len(self.broken)}): " + "; ".join(self.broken[:10]))


def main() -> None:
    o = args()
    docs = Path(o["docs"])
    if not docs.is_dir():
        sys.exit(f"no {docs}/ here")
    Site(docs, Path(o["out"] or docs / "site"), o["title"], o["api"]).build()


if __name__ == "__main__":
    main()
