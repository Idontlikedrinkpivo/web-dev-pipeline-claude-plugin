"""Build a static documentation site from documentation/ (standard library only; Node only for the API page).

    python3 build_site.py [--docs documentation] [--out documentation/_web-docs] [--title "…"] [--no-api | --keep-api]

Every Markdown document becomes a page with the site's navigation, search and cross-links: an id like FR-12,
UC-4, BR-3, NFR-6, TC-27, S-3, З-2 links to the row, heading or screen-spec file that defines it, and an
operationId in backticks links to the API page. Diagrams (.svg) are copied beside their pages. The API page is
Swagger UI (inside the site, works offline) over the contract bundled by Redocly (npx) from
documentation/api/openapi.yaml, or, without Node or network, a table of operations.
documentation/plans/ (working files) is never included. Prints a short report: pages, ids, ids mentioned but never defined,
broken links. The site opens from disk (index.html) — no server needed. It lives in documentation/_web-docs/ and is
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
import urllib.parse
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

OLD_SITES = ("site", "_site")  # the site's folder before 1.2.129 and before 1.2.147: never read as documents

ASSET_EXT = {".svg", ".png", ".jpg", ".jpeg", ".gif", ".webp"}

SWAGGER_PAGE = """<!doctype html><html lang="ru"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>Контракт API — {title}</title>
<link rel="stylesheet" href="../assets/swagger/swagger-ui.css">
<style>
body{margin:0;background:#fafafa}
.bar{position:sticky;top:0;z-index:20;display:flex;align-items:center;gap:16px;height:52px;padding:0 20px;
background:#1f2328;color:#e6e6e6;font:14px -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif}
.bar a{color:#fff;text-decoration:none;font-weight:600}.bar span{color:#9aa1a9}
.swagger-ui .topbar{display:none}.swagger-ui .information-container .info{margin:24px 0 12px}
.swagger-ui .wrapper{max-width:1180px;padding:0 20px}
.swagger-ui .opblock .opblock-summary-operation-id{font-size:12.5px;white-space:nowrap;word-break:normal;flex-shrink:0;
color:#6b7280;margin-left:12px}
.swagger-ui .opblock .opblock-summary-description{min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.swagger-ui .markdown p,.swagger-ui .renderedMarkdown p,.swagger-ui .markdown li,.swagger-ui .renderedMarkdown li{
font:14.5px/1.65 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;color:#2b2f36;max-width:880px}
.swagger-ui .markdown p,.swagger-ui .renderedMarkdown p{margin:0 0 12px}
.swagger-ui .markdown code,.swagger-ui .renderedMarkdown code{background:#eef0f3!important;color:#24292f!important;
font-weight:500!important;font-size:12.5px!important;padding:1px 5px!important;border-radius:4px;border:0!important;
font-family:ui-monospace,SFMono-Regular,Menlo,monospace!important;white-space:nowrap}
.swagger-ui .markdown a,.swagger-ui .renderedMarkdown a{color:#2f5fd0;text-decoration:none;border-bottom:1px dotted #2f5fd0;
white-space:nowrap;position:relative}
.swagger-ui .info{max-width:960px}.swagger-ui .opblock-description-wrapper{padding:14px 20px}
[data-tip]:hover::after{content:attr(data-tip);position:absolute;left:0;bottom:calc(100% + 6px);z-index:50;width:max-content;
max-width:380px;white-space:normal;background:#1f2328;color:#f3f4f6;font:13px/1.45 -apple-system,BlinkMacSystemFont,sans-serif;
padding:8px 10px;border-radius:8px;box-shadow:0 6px 20px rgba(0,0,0,.18);pointer-events:none}
</style></head><body>
<div class="bar"><a href="../index.html">← К документации</a><span>{title} · контракт API</span></div>
<div id="swagger-ui"></div>
<script src="../assets/swagger/swagger-ui-bundle.js"></script><script src="spec.js"></script>
<script>
window.ui = SwaggerUIBundle({
  spec: window.SPEC, dom_id: "#swagger-ui", deepLinking: true, docExpansion: "list",
  defaultModelsExpandDepth: 0, defaultModelExpandDepth: 3, displayOperationId: true, filter: true,
  supportedSubmitMethods: [], tryItOutEnabled: false, syntaxHighlight: {activated: true, theme: "agate"}
});
// a requirement link's title becomes the page's own tooltip (instant, readable) instead of the browser's
new MutationObserver(function () {
  document.querySelectorAll(".swagger-ui .markdown a[title], .swagger-ui .renderedMarkdown a[title]").forEach(function (a) {
    a.setAttribute("data-tip", a.title); a.removeAttribute("title");
  });
}).observe(document.body, {childList: true, subtree: true});
</script></body></html>
"""


def args() -> dict:
    a = sys.argv[1:]
    opt = {"docs": "documentation", "out": None, "title": None, "api": True}
    i = 0
    while i < len(a):
        k = a[i]
        if k in ("--no-api", "--keep-api"):
            opt["api"] = False if k == "--no-api" else "keep"  # keep: reuse the bundled contract (bundling is slow)
            i += 1
            continue
        opt[k.lstrip("-")] = a[i + 1]
        i += 2
    return opt


def plain(s: str) -> str:
    s = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", s)
    return re.sub(r"\s+", " ", re.sub(r"[*`_]|<br\s*/?>", " ", s)).strip()


def summary_of(line: str, ident: str, limit: int = 220) -> str:
    """What a defining line says: a table row's text cells (priority, «—» and the like left out), or the rest of
    a heading or bold lead after the id."""
    if line.lstrip().startswith("|"):
        cells = [plain(c) for c in line.strip().strip("|").split("|")[1:]]
        cells = [c for c in cells if c and c not in ("—", "-") and not re.fullmatch(r"(must|should|could|won't|\d+)", c, re.I)]
        text = " — ".join(cells)
    else:
        text = plain(re.sub(rf"^[#*\s]*{re.escape(ident)}[.:)\s]*", "", line.strip()))
    return text if len(text) <= limit else text[:limit - 1].rsplit(" ", 1)[0] + "…"


def rel(target: str, frm: str) -> str:
    """Relative URL from page `frm` (site path) to site path `target`."""
    return os.path.relpath(target, os.path.dirname(frm) or ".").replace(os.sep, "/")


class Site:
    def __init__(self, docs: Path, out: Path, title: str | None, api: bool):
        self.docs, self.api_on = docs, api
        self.final = out                                         # where the site lives
        self.out = out.parent / f".{out.name}.building"          # built here, then swapped in whole
        self.title = title or self.project_name()
        self.pages: list[dict] = []          # {src, url, section, title, text}
        self.defs: dict[str, str] = {}       # id -> url#anchor (or url)
        self.def_text: dict[str, str] = {}   # id -> what it says, short — shown on hover over a mention
        self.ops: dict[str, str] = {}        # operationId -> "METHOD /path · summary"
        self.op_tags: dict[str, str] = {}    # operationId -> its first tag (Swagger UI links by tag)
        self.mentioned: dict[str, int] = {}
        self.broken: list[str] = []
        self.api_mode = "нет"
        self.out_name = self.final.resolve().relative_to(docs.resolve()).parts[0] \
            if str(self.final.resolve()).startswith(str(docs.resolve()) + os.sep) else None

    def project_name(self) -> str:
        readme = self.docs.parent / "README.md"
        if readme.exists():
            m = re.search(r"^#\s+(.+)$", readme.read_text(encoding="utf-8", errors="replace"), re.M)
            if m:
                return re.sub(r"[`*]", "", m.group(1)).split(" — ")[0].strip()
        try:  # the repository's name, not its folder's: clones in other folders build the same pages
            url = subprocess.run(["git", "-C", str(self.docs), "remote", "get-url", "origin"], capture_output=True,
                                 text=True, timeout=10).stdout.strip()
        except Exception:
            url = ""
        if url:
            return re.sub(r"\.git$", "", url.rstrip("/").split("/")[-1].split(":")[-1])
        return self.docs.resolve().parent.name

    # ---------- collect ----------
    def collect(self) -> None:
        order = {name: i for i, (name, _) in enumerate(SECTIONS)}
        files = []
        for p in sorted(self.docs.rglob("*.md")):
            r = p.relative_to(self.docs)
            top = r.parts[0] if len(r.parts) > 1 else ""
            if top in ("plans", self.out_name, *OLD_SITES) or top.startswith(".") or p.name.startswith("progress"):
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
                self.def_text[m.group(1)] = re.sub(r"^S-\d+\.\s*", "", pg.get("short", pg["title"]))
        for pg in self.pages:
            for line in pg["text"].splitlines():
                m = re.match(rf"^\|\s*[*`]*({ID})[*`]*\s*\|", line) or re.match(rf"^#{{1,6}}\s+[*`]*({ID})\b", line) or re.match(rf"^\*\*({ID})\.", line)
                if m and m.group(1) not in self.defs:
                    self.defs[m.group(1)] = f"{pg['url']}#{m.group(1)}"
                if m and m.group(1) not in self.def_text:
                    self.def_text[m.group(1)] = summary_of(line, m.group(1))

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
                tip = self.def_text.get(i, "")
                attr = f' data-tip="{html.escape(tip)}"' if tip else ""
                return f'<a class="ref" href="{html.escape(href or "#")}"{attr}>{i}</a>'
            return ID_RE.sub(one, text)

        def anchor(text: str) -> str | None:
            t = re.sub(r"[*`]", "", text).strip()
            if pg["rel"].startswith("db/tables/") and re.fullmatch(r"\w+", t) and t not in placed:
                placed.add(t)  # a table document's row is the column it names: users.md#email
                return t
            m = re.match(rf"^({ID})\b", t)
            if m and m.group(1) in anchors_here and m.group(1) not in placed:
                placed.add(m.group(1))
                return m.group(1)
            return None

        def code_link(code: str) -> str | None:
            if (code in self.ops or code in self.op_tags) and self.api_mode != "нет":
                return rel("api/", url).rstrip("/") + "/" + self.op_href(code)[len("api/"):]
            if code.endswith(".md") and " " not in code:
                r = code[len("documentation/"):] if code.startswith("documentation/") else \
                    os.path.normpath(os.path.join(os.path.dirname(pg["rel"]), code)).replace(os.sep, "/")
                if any(p["rel"] == r for p in self.pages):
                    return rel(r[:-3] + ".html", url)
            return None

        return mdhtml.Hooks(link=link, autolink=autolink, anchor=anchor, code_link=code_link)

    def nav_role(self, pg: dict) -> tuple:
        """Where a page goes in the menu: (order in its section, group or None, title, badge). By the document's
        role, not its heading — «Системный анализ (новая версия) — SRS» is the SRS of whatever project."""
        parts, stem = pg["rel"].split("/"), pg["src"].stem
        folders = parts[1:-1]
        end = lambda *names: any(stem == n or stem.endswith("-" + n) for n in names)
        title = pg.get("short", pg["title"])
        if end("open-questions"):
            return 9, None, "Открытые вопросы", ""
        m = re.match(r"^(S-\d+)-", pg["src"].name)
        if m:
            return 2, ("screens", "ТЗ на экраны"), re.sub(r"^S-\d+\.\s*", "", pg["title"]), m.group(1)
        if "test-cases" in folders:
            if stem.lower() in ("readme", "index"):
                return 2.9, ("tests", "Тест-кейсы"), "Обзор", ""  # the group's first item
            return 3, ("tests", "Тест-кейсы"), re.sub(r"\s*\((?:[^()]*\d[^()]*)\)\s*$", "",
                                                      re.sub(r"^\d+\.\s*", "", pg["title"])), ""
        if folders[:1] == ["tables"] and parts[0] == "db":
            return 1, ("tables", "Таблицы"), stem, ""
        if "areas" in folders:
            return 2, ("areas", "Области требований"), title, ""
        if "scenarios" in folders or "scenarios-" in stem:
            name = re.sub(r"^Сценарии\s*[:—-]\s*", "", pg["title"]).strip()
            return 4, ("scenarios", "Сценарии"), name[:1].upper() + name[1:], ""
        for names, order, label in (
                (("business-requirements",), 0, "Бизнес-требования"),
                (("srs",), 1, "Требования к системе (SRS)"),
                (("ui-wishes",), 3, "Пожелания к интерфейсу"),
                (("architecture",), 0, "Основа архитектуры"),
                (("architecture-diagram",), 1, "Схемы архитектуры"),
                (("domain",), 2, "Доменная модель"),
                (("schema",), 0, "Схема БД"),
                (("frames-register", "frames"), 0, "Реестр макетов"),
                (("deploy",), 0, "Инструкция по развёртыванию"),
                (("operations",), 0, "Эксплуатационная документация"),
                (("project-map",), 0, "Карта проекта")):
            if end(*names):
                return order, None, label, ""
        return 5, None, title, ""

    def nav_data(self) -> list:
        """[{label, items}] for assets/nav.js; an item is [url, title, badge] or a group {g, items}. site.js draws
        it, opens the current page's group and marks the page."""
        out = []
        labels = dict(SECTIONS)
        for name, label in SECTIONS + [("", "Прочее")]:
            pages = [p for p in self.pages if (p["section"] or "") == name or (name == "" and p["section"] not in labels)]
            rows = [((-1, 0), None, ["api/index.html", "Контракт API", ""])] if name == "api" and self.api_mode != "нет" else []
            for n, pg in enumerate(pages):
                order, group, title, badge = self.nav_role(pg)
                rows.append(((order, n), group, [pg["url"], title, badge]))
            items, groups = [], {}
            for _, group, item in sorted(rows, key=lambda r: r[0]):
                if group is None:
                    items.append(item)
                elif group[0] in groups:
                    groups[group[0]]["items"].append(item)
                else:
                    groups[group[0]] = {"g": group[1], "items": [item]}
                    items.append(groups[group[0]])
            for g in groups.values():  # a group of one page is just that page
                if len(g["items"]) == 1:
                    items[items.index(g)] = g["items"][0]
            if items:
                out.append({"label": label, "items": items})
        return out

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
        # the site's own commits do not count — nor those of «site», its folder's name before 1.2.129
        spec = ["--", "."] + [f":(exclude){n}" for n in {self.out_name, *OLD_SITES} if n]
        try:
            r = subprocess.run(["git", "-C", str(self.docs), "log", "-1", "--format=%cs · коммит %h"] + spec,
                               capture_output=True, text=True, timeout=10).stdout.strip()
        except Exception:
            r = ""
        self._commit = r or "незакоммиченные изменения"
        return self._commit

    SWAGGER = "5.17.14"  # swagger-ui-dist, pinned; fetched once into the user's cache, then copied into the site

    def swagger_assets(self) -> Path | None:
        cache = Path.home() / ".cache" / "dev-pipeline" / f"swagger-ui-dist-{self.SWAGGER}"
        if (cache / "swagger-ui-bundle.js").exists() and (cache / "swagger-ui.css").exists():
            return cache
        tmp = cache.parent / f".fetch-{os.getpid()}"
        try:
            tmp.mkdir(parents=True, exist_ok=True)
            subprocess.run(["npm", "pack", f"swagger-ui-dist@{self.SWAGGER}", "--pack-destination", str(tmp)],
                           capture_output=True, text=True, timeout=180, check=True)
            subprocess.run(["tar", "-xzf", str(tmp / f"swagger-ui-dist-{self.SWAGGER}.tgz"), "-C", str(tmp)],
                           capture_output=True, timeout=60, check=True)
            cache.mkdir(parents=True, exist_ok=True)
            for f in ("swagger-ui-bundle.js", "swagger-ui.css"):
                shutil.copy(tmp / "package" / f, cache / f)
            return cache
        except Exception:
            return None
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def op_href(self, op: str) -> str:
        """Where an operationId points on the API page (relative to the site root)."""
        if self.api_mode == "Swagger UI":
            tag = self.op_tags.get(op, "default")
            return "api/index.html#/" + urllib.parse.quote(tag, safe="") + "/" + urllib.parse.quote(op, safe="")
        return f"api/index.html#operation/{op}"

    def write_swagger(self, api: Path, doc: dict) -> None:
        """spec.js — the bundled contract with every requirement id in a description turned into a Markdown link to
        its definition, its text as the link's title (shown on hover) — and the page itself."""
        def link(m: re.Match) -> str:
            i = m.group(1)
            d = self.defs.get(i)
            if not d or i[0] in "ЗП":
                return i
            tip = self.def_text.get(i, "").replace('"', "”")
            return f'[{i}](../{d} "{tip}")' if tip else f"[{i}](../{d})"

        def split_cases(item: str) -> list:
            """An item made of several cases joined by «;» (outside brackets and backticks): its lead and cases."""
            parts, depth, tick, cur = [], 0, False, ""
            for ch in item:
                if ch == "`":
                    tick = not tick
                elif not tick and ch in "([{":
                    depth += 1
                elif not tick and ch in ")]}":
                    depth = max(0, depth - 1)
                if ch == ";" and depth == 0 and not tick:
                    parts.append(cur.strip())
                    cur = ""
                else:
                    cur += ch
            parts.append(cur.strip())
            parts = [x for x in parts if x]
            if len(parts) < 3:
                return [item]
            head = parts[0]
            if ":" in head and not head.rstrip().endswith(":"):  # «предел по login разобранного тела: case one»
                lead, first = head.split(":", 1)
                return [lead.strip() + ":", first.strip()] + parts[1:]
            return parts

        def listify(text: str) -> str:
            """«(1) …; (2) …; (3) …» inside a paragraph becomes a numbered list — written that way, a sequence
            of checks reads as one breathless sentence."""
            out = []
            for para in text.split("\n\n"):
                if re.search(r"\(1\)\s", para) and re.search(r"\(2\)\s", para):
                    parts = re.split(r"\s*\((\d+)\)\s+", para)
                    lead, items = parts[0].rstrip(" :—-"), parts[2::2]
                    rows = []
                    for n, it in enumerate(items, 1):
                        cases = split_cases(re.sub(r"[;,]\s*$", "", " ".join(it.split())))
                        rows.append(f"{n}. {cases[0]}" + "".join(f"\n    - {c}" for c in cases[1:]))
                    para = ((lead + ":") if lead else "") + "\n\n" + "\n".join(rows)
                out.append(para)
            return "\n\n".join(out)

        def walk(node):
            if isinstance(node, dict):
                return {k: (ID_RE.sub(link, listify(v)) if k == "description" and isinstance(v, str) else walk(v))
                        for k, v in node.items()}
            if isinstance(node, list):
                return [walk(x) for x in node]
            return node
        (api / "spec.js").write_text("window.SPEC=" + json.dumps(walk(doc), ensure_ascii=False, sort_keys=True) + ";",
                                     encoding="utf-8")
        (api / "index.html").write_text(SWAGGER_PAGE.replace("{title}", html.escape(self.title)), encoding="utf-8")
        self.api_mode = "Swagger UI"

    def build_api(self) -> None:
        """The contract as a Swagger UI page: the spec bundled into one JSON (Redocly), shown read-only («Try it
        out» off — the site has no API behind it), Swagger UI's files inside the site so it works offline. Without
        Node or network: a table of operations."""
        spec = self.docs / "api" / "openapi.yaml"
        self.op_tags: dict = {}
        if not spec.exists() or not self.api_on:
            return
        api, assets = self.out / "api", self.out / "assets" / "swagger"
        api.mkdir(parents=True, exist_ok=True)
        built_api, built_assets = self.final / "api", self.final / "assets" / "swagger"
        if self.api_on == "keep" and (built_api / "openapi.json").exists() and (built_assets / "swagger-ui-bundle.js").exists():
            for f in ("openapi.json", "operations.json"):  # the slow part; the rest is written anew from them
                if (built_api / f).exists():
                    shutil.copy(built_api / f, api / f)
            shutil.copytree(built_assets, assets, dirs_exist_ok=True)
            self.op_tags = json.loads((api / "operations.json").read_text()) if (api / "operations.json").exists() else {}
            self.write_swagger(api, json.loads((api / "openapi.json").read_text()))
            return
        swagger = self.swagger_assets()
        bundled = api / ".openapi.json"
        try:
            r = subprocess.run(["npx", "--yes", "@redocly/cli@latest", "bundle", str(spec), "--ext", "json",
                                "-o", str(bundled)], capture_output=True, text=True, timeout=300)
            doc = json.loads(bundled.read_text()) if r.returncode == 0 and bundled.exists() else None
        except Exception:
            doc = None
        finally:
            bundled.unlink(missing_ok=True) if bundled.exists() else None
        if doc and swagger:
            for path_item in (doc.get("paths") or {}).values():
                for method, op in path_item.items():
                    if isinstance(op, dict) and op.get("operationId"):
                        self.op_tags[op["operationId"]] = (op.get("tags") or ["default"])[0]
            assets.mkdir(parents=True, exist_ok=True)
            for f in ("swagger-ui-bundle.js", "swagger-ui.css"):
                shutil.copy(swagger / f, assets / f)
            (api / "openapi.json").write_text(json.dumps(doc, ensure_ascii=False, sort_keys=True, indent=1), encoding="utf-8")
            (api / "operations.json").write_text(json.dumps(self.op_tags, ensure_ascii=False, sort_keys=True, indent=0),
                                                 encoding="utf-8")
            self.write_swagger(api, doc)
            return
        rows = "".join(f'<tr id="operation/{html.escape(o)}"><td><code>{html.escape(o)}</code></td>'
                       f"<td>{html.escape(d)}</td></tr>" for o, d in sorted(self.ops.items(), key=lambda x: x[1]))
        body = (f"<h1>Контракт API</h1><p>Полный контракт — <code>documentation/api/openapi.yaml</code>. "
                f"Здесь — список операций: интерактивная страница не собрана (нет Node.js или сети).</p>"
                f'<div class="table"><table><thead><tr><th>operationId</th><th>Операция</th></tr></thead>'
                f"<tbody>{rows}</tbody></table></div>")
        (api / "index.html").write_text(self.page("api/index.html", "Контракт API", body, [], {}), encoding="utf-8")
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
            if p.suffix.lower() in ASSET_EXT and r.parts[0] not in ("plans", self.out_name, *OLD_SITES) \
                    and not r.parts[0].startswith("."):
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
        old = self.final.parent / f".{self.final.name}.old"
        if old.exists():
            shutil.rmtree(old)
        if self.final.exists():
            self.final.rename(old)
        self.out.rename(self.final)  # a reader never sees a half-built site
        if old.exists():
            shutil.rmtree(old)
        self.out = self.final
        self.report()

    def home(self) -> None:
        counts = []
        for k in KINDS:
            n = sum(1 for i in self.defs if i.split("-")[0] == k)
            if n:
                counts.append(f"<div><b>{n}</b><span>{KIND_LABEL[k]}</span></div>")
        body = (f'<h1>{html.escape(self.title)}</h1><p class="lead">Документация проекта: требования, данные, API, '
                f'архитектура, интерфейс и эксплуатация. Номера требований, сценариев, тест-кейсов и экранов — '
                f'ссылки на их определение; разделы — в меню слева, поиск — вверху страницы.</p>'
                f'<div class="counts">{"".join(counts)}</div>')
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
    Site(docs, Path(o["out"] or docs / "_web-docs"), o["title"], o["api"]).build()


if __name__ == "__main__":
    main()
