"""One document per database table, generated from the DBML of the schema document.

    python3 table_docs.py [<project root>]     # writes documentation/db/tables/<table>.md, prints what changed

Reads every ```dbml block of the Markdown files under documentation/db/ (the tables/ folder left out) and the
rows of `## Закрытые наборы значений` (`## Status attributes` before 1.2.152): `table.column` → code → label. For each table: its Note, one row per column —
Поле · Тип данных · Свойства (PRIMARY KEY, FOREIGN KEY, UNIQUE, NOT NULL / NULL) · Значение по умолчанию ·
Связь (a link to the referenced table's column) · Допустимые значения (closed-set codes, single-column CHECKs) ·
Описание (the first sentence of the column's note) — then the incoming references with what deleting a row does,
and the rules over several columns. The documents are a view of the schema: edit schema.md, never them; a file
that carries the marker and names a table no longer in the schema is removed. Deterministic: an unchanged schema
rewrites no file. Standard library only.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

MARK = "<!-- Собрано из {src} скриптом db-schema-design/scripts/table_docs.py. Правьте схему, не этот файл. -->"
DELETE = {
    "cascade": "удаляются вместе с ней (CASCADE)",
    "restrict": "удалить нельзя, пока на неё ссылается такая запись (RESTRICT)",
    "no action": "удалить нельзя, пока на неё ссылается такая запись (NO ACTION)",
    "set null": "поле становится пустым (SET NULL)",
    "set default": "поле получает значение по умолчанию (SET DEFAULT)",
}


def split_top(s: str, sep: str = ",") -> list[str]:
    """Split on sep outside quotes, backticks and brackets."""
    out, buf, q, depth, i = [], "", "", 0, 0
    while i < len(s):
        c = s[i]
        if q:
            buf += c
            if c == "\\" and i + 1 < len(s):
                buf += s[i + 1]
                i += 1
            elif s.startswith(q, i):
                buf += s[i + 1:i + len(q)]
                i += len(q) - 1
                q = ""
        elif s.startswith("'''", i):
            q, buf, i = "'''", buf + "'''", i + 2
        elif c in "'`\"":
            q, buf = c, buf + c
        elif c in "([{":
            depth, buf = depth + 1, buf + c
        elif c in ")]}":
            depth, buf = depth - 1, buf + c
        elif c == sep and depth == 0:
            out.append(buf.strip())
            buf = ""
        else:
            buf += c
        i += 1
    if buf.strip():
        out.append(buf.strip())
    return out


def unquote(v: str) -> str:
    v = v.strip()
    for q in ("'''", "'", '"'):
        if len(v) >= 2 * len(q) and v.startswith(q) and v.endswith(q):
            return v[len(q):-len(q)].replace("\\'", "'")
    return v


def bracket(line: str) -> tuple[str, str]:
    """'name type [settings]' → ('name type', 'settings'); the bracket may hold quoted ']'."""
    depth, q = 0, ""
    for i, c in enumerate(line):
        if q:
            if c == q and line[i - 1] != "\\":
                q = ""
        elif c in "'`\"":
            q = c
        elif c == "[":
            if depth == 0:
                start = i
            depth += 1
        elif c == "]":
            depth -= 1
            if depth == 0:
                return line[:start].strip(), line[start + 1:i]
    return line.strip(), ""


def settings(s: str) -> dict:
    out: dict = {}
    for part in split_top(s):
        k, sep, v = part.partition(":")
        k = k.strip().lower()
        out[k] = v.strip() if sep else True
    return out


def short(name: str) -> str:
    return unquote(name).split(".")[-1].strip('"')


def blocks(text: str) -> list[str]:
    return re.findall(r"^```dbml\s*\n(.*?)^```", text, re.S | re.M)


def parse(dbml: str, tables: dict, refs: list) -> None:
    lines = dbml.split("\n")
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        m = re.match(r"^Table\s+([\w.\"]+)(?:\s+as\s+\w+)?\s*(\[.*\])?\s*\{\s*$", line, re.I)
        if m:
            name = short(m.group(1))
            t = tables.setdefault(name, {"cols": [], "note": "", "checks": [], "indexes": []})
            if m.group(2):
                note = settings(m.group(2)[1:-1]).get("note")
                if note:
                    t["note"] = unquote(note)
            i += 1
            sub = None
            while i < len(lines):
                raw = lines[i]
                ln = raw.strip()
                if not ln or ln.startswith("//"):
                    i += 1
                    continue
                if sub:
                    if ln == "}":
                        sub = None
                    else:
                        t[sub].append(bracket(ln))
                    i += 1
                    continue
                if ln == "}":
                    break
                low = ln.lower()
                if low.startswith(("indexes", "checks")) and ln.endswith("{"):
                    sub = "indexes" if low.startswith("indexes") else "checks"
                elif low.startswith("note"):
                    body = ln.split(":", 1)[1].strip() if ":" in ln else ""
                    if body.startswith("'''") and not (len(body) > 6 and body.endswith("'''")):
                        while i + 1 < len(lines) and "'''" not in lines[i + 1]:
                            i += 1
                            body += "\n" + lines[i]
                        i += 1
                        body += "\n" + lines[i]
                    t["note"] = unquote(body.strip())
                else:
                    head, sets = bracket(ln)
                    parts = head.split(None, 1)
                    if len(parts) == 2:
                        t["cols"].append({"name": parts[0].strip('"'), "type": unquote(parts[1]),
                                          "set": settings(sets)})
                        ref = t["cols"][-1]["set"].get("ref")
                        if ref:
                            rm = re.match(r"^([<>-])\s*([\w.\"]+)", ref)
                            if rm:
                                target = rm.group(2).split(".")
                                refs.append({"from": (name, parts[0].strip('"')),
                                             "to": (short(".".join(target[:-1])), target[-1].strip('"')),
                                             "op": rm.group(1), "delete": ""})
                i += 1
        else:
            rm = re.match(r"^Ref(?:\s+\w+)?\s*:\s*([\w.\"]+)\s*([<>-])\s*([\w.\"]+)\s*(\[.*\])?", line, re.I)
            if rm:
                a, op, b = rm.group(1).split("."), rm.group(2), rm.group(3).split(".")
                left, right = (short(".".join(a[:-1])), a[-1].strip('"')), (short(".".join(b[:-1])), b[-1].strip('"'))
                if op == "<":
                    left, right = right, left
                sets = settings(rm.group(4)[1:-1]) if rm.group(4) else {}
                refs.append({"from": left, "to": right, "op": op, "delete": str(sets.get("delete", "")).lower()})
        i += 1


def statuses(text: str) -> dict:
    """`table.column` → ['`code` — label', …] from the closed-set table, whatever its heading."""
    out: dict = {}
    for m in re.finditer(r"^\|\s*`(\w+)\.(\w+)`\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|\s*$", text, re.M):
        code, label = m.group(3), m.group(4)
        out.setdefault((m.group(1), m.group(2)), []).append(code if label in ("", "—") else f"{code} — {label}")
    return out


def first_sentence(note: str) -> str:
    note = " ".join(note.split())
    m = re.match(r"^(.+?[.!?])(?=\s+[A-ZА-ЯЁ«(`]|$)", note)
    s = m.group(1) if m else note
    return s.rstrip(".")


def cell(s: str) -> str:
    return s.replace("|", "\\|").replace("\n", " ")


def table_doc(name: str, t: dict, refs: list, codes: dict, src: str) -> str:
    cols = {c["name"] for c in t["cols"]}
    unique_extra: dict = {}
    multi: list = []
    for head, sets in t["indexes"]:
        st = settings(sets)
        if not st.get("unique") and not st.get("pk"):
            continue
        expr = head.strip()
        inner = expr[1:-1].strip() if expr.startswith("(") and expr.endswith(")") else expr
        names = [c for c in re.findall(r"\b\w+\b", inner) if c in cols]
        if re.fullmatch(r"\w+", inner) and inner in cols:
            unique_extra.setdefault(inner, []).append("UNIQUE")
        elif len(set(names)) == 1 and "," not in inner:
            unique_extra.setdefault(names[0], []).append(f"UNIQUE (`{inner}`)")
        else:
            multi.append(f"уникальны вместе: `{inner}`")
    allowed: dict = {}
    for head, sets in t["checks"]:
        expr = head.strip().strip("`")
        names = sorted({c for c in re.findall(r"\b\w+\b", expr) if c in cols})
        nm = unquote(str(settings(sets).get("name", "")))
        if len(names) == 1:
            if (name, names[0]) in codes and re.search(r"\bIN\s*\(", expr, re.I):
                continue  # the closed set is already listed by its codes
            allowed.setdefault(names[0], []).append(f"`{expr}`" if len(expr) <= 60 or not nm else f"проверка `{nm}`")
        else:
            multi.append(f"проверка `{expr}`" + (f" ({nm})" if nm else ""))
    out_refs = {r["from"][1]: r for r in refs if r["from"][0] == name}
    rows = []
    for c in t["cols"]:
        s = c["set"]
        props = []
        if s.get("pk") or s.get("primary key"):
            props.append("PRIMARY KEY")
        if c["name"] in out_refs:
            props.append("FOREIGN KEY")
        if s.get("unique"):
            props.append("UNIQUE")
        props += unique_extra.get(c["name"], [])
        if not (s.get("pk") or s.get("primary key")):
            props.append("NOT NULL" if s.get("not null") else "NULL")
        if s.get("increment"):
            default = "автонумерация"
        elif "default" in s:
            d = str(s["default"]).strip()
            default = f"`{d.strip('`')}`"
        else:
            default = "—"
        r = out_refs.get(c["name"])
        link = f"[`{r['to'][0]}.{r['to'][1]}`]({r['to'][0]}.md#{r['to'][1]})" if r else "—"
        vals = [f"`{v}`" if not v.startswith("`") else v for v in codes.get((name, c["name"]), [])]
        vals += allowed.get(c["name"], [])
        desc = first_sentence(unquote(str(s.get("note", "")))) if s.get("note") else ""
        rows.append(f"| `{c['name']}` | {cell(c['type'])} | {', '.join(props)} | {cell(default)} | {link} | "
                    f"{cell('; '.join(vals)) or '—'} | {cell(desc) or '—'} |")
    parts = [MARK.format(src=src), "", f"# {name}", ""]
    if t["note"]:
        parts += [" ".join(t["note"].split()), ""]
    parts += ["| Поле | Тип данных | Свойства | Значение по умолчанию | Связь | Допустимые значения | Описание |",
              "|---|---|---|---|---|---|---|", *rows, ""]
    incoming = sorted((r for r in refs if r["to"][0] == name), key=lambda r: (r["from"][0], r["from"][1]))
    if incoming:
        parts += ["## Входящие связи", "",
                  f"| Поле | Ссылается на | Если удалить запись из `{name}` |", "|---|---|---|"]
        for r in incoming:
            act = DELETE.get(r["delete"] or "no action", r["delete"])
            parts.append(f"| [`{r['from'][0]}.{r['from'][1]}`]({r['from'][0]}.md#{r['from'][1]}) | "
                         f"`{r['to'][1]}` | {act} |")
        parts.append("")
    if multi:
        parts += ["## Правила на несколько полей", ""] + [f"- {m};" for m in multi[:-1]] + [f"- {multi[-1]}."] + [""]
    return "\n".join(parts)


def main() -> None:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    db = root / "documentation" / "db"
    out_dir = db / "tables"
    tables: dict = {}
    refs: list = []
    codes: dict = {}
    src = None
    for f in sorted(db.rglob("*.md")) if db.is_dir() else []:
        if out_dir in f.parents:
            continue
        text = f.read_text(encoding="utf-8")
        found = blocks(text)
        if found:
            src = src or f.relative_to(root / "documentation").as_posix()
            for b in found:
                parse(b, tables, refs)
            codes.update(statuses(text))
    if not tables:
        print("no DBML under documentation/db — nothing to write")
        return
    out_dir.mkdir(parents=True, exist_ok=True)
    changed = []
    for name, t in tables.items():
        p = out_dir / f"{name}.md"
        text = table_doc(name, t, refs, codes, src)
        if not p.exists() or p.read_text(encoding="utf-8") != text:
            p.write_text(text, encoding="utf-8")
            changed.append(p.name)
    for p in sorted(out_dir.glob("*.md")):
        if p.stem not in tables and p.read_text(encoding="utf-8").startswith("<!-- Собрано из"):
            p.unlink()
            changed.append(f"{p.name} (removed)")
    print(f"tables: {len(tables)} in documentation/db/tables/; changed: {', '.join(changed) or 'none'}")


if __name__ == "__main__":
    main()
