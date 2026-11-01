#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Every environment's variables file built from one template, `.env.example` — so test, dev and prod list the same
variables, in the same order, with the same comments, and differ only in their values.

    python3 env_files.py [<project dir>] build    write the files below from the template
    python3 env_files.py [<project dir>] check    exit 1 when a file differs from the template in names or order

The template (deploy-topology → references/env-and-config-contract.md → Markers in `.env.example`): each key with the
comment line right above it, its markers first — `[required]`, `[secret]`, `[infra]` — and, at the end of that line,
the values that differ by environment: `{test: <value>, dev: <value>, prod: <value>}`; `—` means «not in this
environment». The key's own value is the one every environment not named gets. A blank line and the comments after
it (a section heading) are kept as they are; the comments before the first blank line are the template's own head
(«compose does not read this file») and are not copied.

Built:
  .env.test.local, .env.dev.local      (gitignored) — for each environment with a docker-compose.<env>.yml or a
                                       file already there: the template's order and comments, that environment's
                                       non-secret values; a secret keeps the value the file already has (never
                                       printed), a new one is empty to fill in;
  documentation/deploy/prod.env.example — the operators' file: prod values, secrets empty, no `[infra]` key (an
                                       older project's deploy/prod.env.example in its place).
A key a file had and the template does not is dropped and named; a non-secret value that changed is named with the
old and the new value. Standard library only.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

KEY = re.compile(r"^([A-Z][A-Z0-9_]*)=(.*)$")
MAP = re.compile(r"\s*\{((?:test|dev|prod)\s*:.*)\}\s*$")
PART = re.compile(r"(test|dev|prod)\s*:\s*(.*?)(?=,\s*(?:test|dev|prod)\s*:|$)")
ABSENT = {"—", "-", "–"}
HEAD = ("# Собрано из .env.example скриптом deploy-topology/scripts/env_files.py для среды «{env}». Правьте шаблон\n"
        "# и пересоберите: `python3 <deploy-topology>/scripts/env_files.py . build`{secrets}\n\n")


def parse(text: str) -> list[dict]:
    """The template as items in order: {"text": [lines]} for free comments, {"key", "value", "comments", "markers",
    "per_env"} for a variable."""
    items: list[dict] = []
    buf: list[str] = []
    for line in text.splitlines():
        m = KEY.match(line)
        if m:
            above = buf[-1] if buf else ""
            markers = set(re.findall(r"\[(required|secret|infra)\]", above))
            per_env = {}
            mm = MAP.search(above)
            if mm:
                per_env = {e: v.strip() for e, v in PART.findall(mm.group(1))}
                buf = buf[:-1] + [above[:mm.start()].rstrip()]
            items.append({"key": m.group(1), "value": m.group(2), "comments": buf, "markers": markers,
                          "per_env": per_env})
            buf = []
        elif not line.strip():
            if buf:   # the comments before the first blank line are the template's own head: not copied
                items.append({"head": buf} if not items else {"text": buf})
            items.append({"text": [""]})
            buf = []
        else:
            buf.append(line)
    if buf:
        items.append({"text": buf})
    return items


def values(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    return {m.group(1): m.group(2) for m in (KEY.match(l) for l in path.read_text(encoding="utf-8").splitlines()) if m}


def keys_for(items: list[dict], env: str) -> list[dict]:
    out = []
    for it in items:
        if "key" not in it:
            continue
        v = it["per_env"].get(env, it["value"])
        if v in ABSENT or (env == "prod" and "infra" in it["markers"]):
            continue
        out.append(it)
    return out


def render(items: list[dict], env: str, old: dict[str, str]) -> tuple[str, list[str]]:
    keep = {it["key"] for it in keys_for(items, env)}
    lines, notes = [], []
    for it in items:
        if "head" in it:
            continue
        if "text" in it:
            lines += it["text"]
            continue
        if it["key"] not in keep:
            continue
        secret = "secret" in it["markers"]
        if secret:
            v = "" if env == "prod" else old.get(it["key"], "")
        else:
            v = it["per_env"].get(env, it["value"])
            if it["key"] in old and old[it["key"]] != v:
                notes.append(f"{it['key']}: «{old[it['key']]}» → «{v}»")
        if it["key"] not in old and old:
            notes.append(f"{it['key']}: добавлена" + (" — секрет, впишите значение" if secret and env != "prod" else ""))
        lines += it["comments"] + [f"{it['key']}={v}"]
    gone = [k for k in old if k not in keep]
    notes += [f"{k}: убрана — её нет в шаблоне для этой среды" for k in gone]
    text = "\n".join(lines).strip("\n") + "\n"
    while "\n\n\n" in text:
        text = text.replace("\n\n\n", "\n\n")
    return text, notes


def targets(root: Path) -> dict[str, Path]:
    out = {}
    for env in ("test", "dev"):
        local = root / f".env.{env}.local"
        if local.exists() or (root / f"docker-compose.{env}.yml").exists():
            out[env] = local
    docs, old = root / "documentation" / "deploy" / "prod.env.example", root / "deploy" / "prod.env.example"
    if old.exists() and not docs.exists():   # an older project keeps it in deploy/
        out["prod"] = old
    elif docs.parent.is_dir() or (root / "docker-compose.prod.yml").exists():
        out["prod"] = docs
    return out


def main() -> None:
    args = sys.argv[1:]
    mode = next((a for a in args if a in ("build", "check")), None)
    root = Path(next((a for a in args if a not in ("build", "check")), ".")).resolve()
    template = root / ".env.example"
    if not mode or not template.exists():
        sys.exit(__doc__ if not mode else f"env_files: нет шаблона {template}")
    items = parse(template.read_text(encoding="utf-8"))
    problems = 0
    for env, path in targets(root).items():
        secrets = "; секреты вписываются сюда и при пересборке\n# сохраняются" if env != "prod" else \
                  "; значений секретов здесь нет —\n# их заполняет эксплуатация"
        text, notes = render(items, env, values(path))
        text = HEAD.format(env=env, secrets=secrets) + text
        rel = path.relative_to(root)
        if mode == "build":
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
            print(f"env_files: {rel} — {len(keys_for(items, env))} переменных" + (": " + "; ".join(notes) if notes else ""))
            continue
        want = [it["key"] for it in keys_for(items, env)]
        have = list(values(path)) if path.exists() else None
        if have is None:
            print(f"✗ {rel}: файла нет — env_files.py . build")
            problems += 1
        elif have != want:
            missing = [k for k in want if k not in have]
            extra = [k for k in have if k not in want]
            what = (["нет: " + ", ".join(missing)] if missing else []) + (["лишние: " + ", ".join(extra)] if extra else [])
            print(f"✗ {rel}: не совпадает с шаблоном — " + ("; ".join(what) or "другой порядок") + " — env_files.py . build")
            problems += 1
    if mode == "check":
        print("env_files: все файлы совпадают с шаблоном" if not problems else f"env_files: расхождений {problems}")
        sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
