"""A small Markdown -> HTML converter for the documents this plugin writes (standard library only).

Covers what the templates use: YAML frontmatter, ATX headings, paragraphs, fenced code, tables, nested lists,
blockquotes, horizontal rules, raw HTML lines, and inline code, bold, italic, links and images. Not a full
CommonMark implementation: an unusual construct falls back to a paragraph.

Hooks let a caller rewrite links (`.md` -> `.html`), link ids in text (`FR-12` -> its definition) and place
anchors on the rows and headings that define an id.
"""
from __future__ import annotations

import html
import re
from dataclasses import dataclass, field
from typing import Callable, Optional

Link = Callable[[str], str]                 # href -> href
Autolink = Callable[[str], str]             # escaped text -> text with <a> around known ids
Anchor = Callable[[str], Optional[str]]     # cell or heading text -> anchor id or None
CodeLink = Callable[[str], Optional[str]]   # inline code text -> href or None


@dataclass
class Hooks:
    link: Link = lambda h: h
    autolink: Autolink = lambda t: t
    anchor: Anchor = lambda t: None
    code_link: CodeLink = lambda t: None


@dataclass
class Result:
    html: str
    headings: list = field(default_factory=list)   # (level, text, slug)
    meta: dict = field(default_factory=dict)


def split_frontmatter(text: str) -> tuple[dict, str]:
    m = re.match(r"---\n(.*?)\n---\n", text, re.S)
    if not m:
        return {}, text
    meta = {}
    for line in m.group(1).splitlines():
        if ":" in line and not line.startswith((" ", "-", "#")):
            k, v = line.split(":", 1)
            meta[k.strip()] = v.strip().strip('"').strip("'")
    return meta, text[m.end():]


def slug(text: str, used: dict) -> str:
    s = re.sub(r"<[^>]+>", "", text).lower()
    s = re.sub(r"[^\w\s-]", "", s, flags=re.U).strip()
    s = re.sub(r"[\s_]+", "-", s) or "section"
    n = used.get(s, 0)
    used[s] = n + 1
    return s if n == 0 else f"{s}-{n}"


# ---------- inline ----------

def inline(text: str, hooks: Hooks, autolink: bool = True) -> str:
    keep: list[str] = []

    def stash(s: str) -> str:
        keep.append(s)
        return f"\x00{len(keep) - 1}\x00"

    def code(m: re.Match) -> str:
        body = m.group(2)
        tag = f"<code>{html.escape(body)}</code>"
        href = hooks.code_link(body)
        return stash(f'<a href="{html.escape(href)}">{tag}</a>' if href else tag)

    text = re.sub(r"(`+)(.+?)\1", code, text)

    def image(m: re.Match) -> str:
        alt, src = m.group(1), hooks.link(m.group(2).strip().split(" ")[0])
        return stash(f'<img src="{html.escape(src)}" alt="{html.escape(alt)}" loading="lazy">')

    text = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", image, text)

    def link(m: re.Match) -> str:
        label, href = m.group(1), hooks.link(m.group(2).strip().split(" ")[0])
        ext = ' target="_blank" rel="noopener"' if href.startswith(("http://", "https://")) else ""
        # a label whose code was already stashed («[`users.id`](users.md#id)») keeps its placeholders: the loop
        # at the end resolves them; rendering it again would look them up in a list of its own
        inner = html.escape(label, quote=False) if "\x00" in label else inline(label, hooks, autolink=False)
        return stash(f'<a href="{html.escape(href)}"{ext}>{inner}</a>')

    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", link, text)
    text = re.sub(r"<(https?://[^>\s]+)>", lambda m: stash(
        f'<a href="{html.escape(m.group(1))}" target="_blank" rel="noopener">{html.escape(m.group(1))}</a>'), text)
    text = re.sub(r"<br\s*/?>", lambda m: stash("<br>"), text)
    text = re.sub(r"</?su[bp]>", lambda m: stash(m.group(0)), text)

    text = html.escape(text, quote=False)
    if autolink:
        text = hooks.autolink(text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<em>\1</em>", text)
    text = re.sub(r"~~(.+?)~~", r"<del>\1</del>", text)
    while "\x00" in text:
        text = re.sub(r"\x00(\d+)\x00", lambda m: keep[int(m.group(1))], text)
    return text


# ---------- blocks ----------

def split_row(line: str) -> list[str]:
    line = line.strip()
    if line.startswith("|"):
        line = line[1:]
    if line.endswith("|") and not line.endswith("\\|"):
        line = line[:-1]
    cells, cur, in_code = [], "", False
    for i, ch in enumerate(line):
        if ch == "`":
            in_code = not in_code
        if ch == "|" and not in_code and (i == 0 or line[i - 1] != "\\"):
            cells.append(cur)
            cur = ""
        else:
            cur += ch
    cells.append(cur)
    return [c.strip().replace("\\|", "|") for c in cells]


def is_sep(line: str) -> bool:
    return bool(re.match(r"^\s*\|?\s*:?-{2,}:?\s*(\|\s*:?-{2,}:?\s*)*\|?\s*$", line))


LIST = re.compile(r"^(\s*)([-*+]|\d+[.)])\s+(.*)$")


class Converter:
    def __init__(self, hooks: Hooks):
        self.hooks = hooks
        self.headings: list = []
        self.used: dict = {}

    def blocks(self, lines: list[str]) -> str:
        out, i = [], 0
        while i < len(lines):
            line = lines[i]
            s = line.strip()
            if not s:
                i += 1
                continue
            fence = re.match(r"^(\s*)(`{3,}|~{3,})(.*)$", line)
            if fence:
                mark, lang = fence.group(2), fence.group(3).strip()
                j = i + 1
                while j < len(lines) and not lines[j].strip().startswith(mark):
                    j += 1
                body = "\n".join(l[len(fence.group(1)):] if l.startswith(fence.group(1)) else l for l in lines[i + 1:j])
                cls = f' class="language-{html.escape(lang.split()[0])}"' if lang else ""
                out.append(f"<pre><code{cls}>{html.escape(body)}</code></pre>")
                i = j + 1
                continue
            h = re.match(r"^(#{1,6})\s+(.*?)\s*#*\s*$", line)
            if h:
                level, text = len(h.group(1)), h.group(2)
                anchor = self.hooks.anchor(text)
                sid = slug(text, self.used)
                self.headings.append((level, re.sub(r"[`*]", "", text), sid))
                extra = f'<span class="anchor" id="{html.escape(anchor)}"></span>' if anchor else ""
                out.append(f'<h{level} id="{sid}">{extra}{inline(text, self.hooks, autolink=False)}'
                           f'<a class="hash" href="#{sid}">#</a></h{level}>')
                i += 1
                continue
            if re.match(r"^\s*([-*_])(\s*\1){2,}\s*$", line):
                out.append("<hr>")
                i += 1
                continue
            if s.startswith("|") and i + 1 < len(lines) and is_sep(lines[i + 1]):
                j = i + 2
                while j < len(lines) and lines[j].strip().startswith("|"):
                    j += 1
                out.append(self.table(lines[i], lines[i + 2:j]))
                i = j
                continue
            if s.startswith(">"):
                j = i
                quoted = []
                while j < len(lines) and lines[j].strip().startswith(">"):
                    quoted.append(re.sub(r"^\s*>\s?", "", lines[j]))
                    j += 1
                out.append(f"<blockquote>{self.blocks(quoted)}</blockquote>")
                i = j
                continue
            if LIST.match(line):
                html_list, i = self.list_block(lines, i)
                out.append(html_list)
                continue
            if s.startswith("<") and re.match(r"^<(/?)(details|summary|div|table|p|br|img|svg|figure)\b", s):
                out.append(line)
                i += 1
                continue
            para = [s]
            i += 1
            while i < len(lines):
                n = lines[i]
                if (not n.strip() or n.lstrip().startswith(("#", ">", "```", "~~~", "|")) or LIST.match(n)
                        or re.match(r"^\s*([-*_])(\s*\1){2,}\s*$", n)):
                    break
                para.append(n.strip())
                i += 1
            text = "\n".join(para)
            text = re.sub(r"(\s{2}|\\)\n", "<br>", text)
            text = re.sub(r"\n(?=\*\*[^*\n]{1,40}:\*\*)", "<br>", text)  # «**Кто:** …» under «**Проверяет:** …»
            pid = self.hooks.anchor(text) if text.startswith("**") else None  # «**З-2. …**» defines З-2
            pattr = ' id="%s"' % html.escape(pid) if pid else ""
            out.append(f"<p{pattr}>{inline(text, self.hooks)}</p>")
        return "\n".join(out)

    def table(self, head: str, rows: list[str]) -> str:
        hs = split_row(head)
        parts = ["<div class=\"table\"><table><thead><tr>"]
        parts += [f"<th>{inline(c, self.hooks)}</th>" for c in hs]
        parts.append("</tr></thead><tbody>")
        for r in rows:
            cells = split_row(r)
            anchor = self.hooks.anchor(cells[0]) if cells else None
            rid = f' id="{html.escape(anchor)}"' if anchor else ""
            parts.append(f"<tr{rid}>" + "".join(f"<td>{inline(c, self.hooks)}</td>" for c in cells) + "</tr>")
        parts.append("</tbody></table></div>")
        return "".join(parts)

    def list_block(self, lines: list[str], i: int) -> tuple[str, int]:
        first = LIST.match(lines[i])
        indent = len(first.group(1))
        ordered = first.group(2)[0].isdigit()
        items: list[list[str]] = []
        while i < len(lines):
            line = lines[i]
            m = LIST.match(line)
            if m and len(m.group(1)) == indent:
                items.append([m.group(3)])
                i += 1
                continue
            if not line.strip():
                if i + 1 < len(lines) and (lines[i + 1].startswith(" " * (indent + 2)) or
                                           (LIST.match(lines[i + 1]) and len(LIST.match(lines[i + 1]).group(1)) >= indent)):
                    items[-1].append("")
                    i += 1
                    continue
                break
            if len(line) - len(line.lstrip()) > indent:
                items[-1].append(line[indent + 2:] if line.startswith(" " * (indent + 2)) else line.strip())
                i += 1
                continue
            break
        tag = "ol" if ordered else "ul"
        body = []
        for it in items:
            head, rest = it[0], it[1:]
            box = ""
            cm = re.match(r"^\[([ xX])\]\s+(.*)$", head)
            if cm:
                box = '<input type="checkbox" disabled' + (" checked" if cm.group(1) != " " else "") + "> "
                head = cm.group(2)
            if any(r.strip() for r in rest):
                inner = self.blocks([head] + rest) if not LIST.match(rest[0] if rest else "") else (
                    f"{inline(head, self.hooks)}" + self.blocks(rest))
                if inner.startswith("<p>") and inner.count("<p>") == 1:
                    inner = inner[3:].replace("</p>", "", 1)
                body.append(f"<li>{box}{inner}</li>")
            else:
                body.append(f"<li>{box}{inline(head, self.hooks)}</li>")
        return f"<{tag}>" + "".join(body) + f"</{tag}>", i


def convert(text: str, hooks: Optional[Hooks] = None) -> Result:
    meta, body = split_frontmatter(text)
    body = re.sub(r"<!--.*?-->", "", body, flags=re.S)  # comments are notes for the writer, not the reader
    c = Converter(hooks or Hooks())
    out = c.blocks(body.replace("\r\n", "\n").split("\n"))
    return Result(out, c.headings, meta)
