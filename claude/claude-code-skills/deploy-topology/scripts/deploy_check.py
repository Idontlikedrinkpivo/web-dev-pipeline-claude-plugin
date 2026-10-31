#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Check the container files and the release folder against deploy-topology → Before you finish — what code can
decide, so the stage closes on facts.

    python3 deploy_check.py [<project dir>] [--version <v>]

  compose     docker-compose.{dev,test,prod}.yml all exist. In test and prod, every service built from the project
              (`build:`) runs read_only, with /tmp as tmpfs, cap_drop ALL and no-new-privileges; `backend` has a
              healthcheck on /health/ready; prod runs no local stateful service (Postgres, MySQL, Redis, MinIO, …).
  images      every Dockerfile the compose files build: the stage they build ends with a numeric USER other than 0;
              a .dockerignore sits in the build context.
  release     release/<version>/ (the given version, else the newest) holds a .tar, DEPLOY.md, an .env.example and
              one openapi.yaml; every file name DEPLOY.md cites in backticks is in that folder.

Exit 0 — clean; 1 — a line per problem. Run at deploy-topology's close (Before you finish). A parser of the compose
shape this skill writes, not of all YAML: an unusual layout it cannot read is reported, never passed silently.
Standard library only.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

STATEFUL = re.compile(r"\b(postgres|postgis|mysql|mariadb|mongo|redis|valkey|minio|rabbitmq|kafka|elasticsearch|"
                      r"opensearch|clickhouse|cassandra)\b", re.I)


def services(text: str) -> dict[str, str]:
    """service name -> its block, from the top-level `services:` map (two-space indent, as this skill writes)."""
    m = re.search(r"^services:\s*\n(.*?)(?=^\S|\Z)", text, re.M | re.S)
    if not m:
        return {}
    out, name, buf = {}, None, []
    for line in m.group(1).splitlines():
        head = re.match(r"^  ([A-Za-z0-9_.-]+):\s*$", line)
        if head:
            if name:
                out[name] = "\n".join(buf)
            name, buf = head.group(1), []
        elif name:
            buf.append(line)
    if name:
        out[name] = "\n".join(buf)
    return out


def key_block(block: str, key: str) -> str:
    """The value of `key:` in a service block — inline, or the lines indented under it."""
    m = re.search(rf"^    {key}:(.*)$", block, re.M)
    if not m:
        return ""
    lines = [m.group(1)]
    for line in block[m.end():].splitlines()[1:]:
        if line.startswith("      ") or not line.strip() or line.strip().startswith("#"):
            lines.append(line)
        else:
            break
    return "\n".join(lines)


def check_compose(root: Path, out: list) -> list[tuple[str, str, str]]:
    builds = []
    for env in ("dev", "test", "prod"):
        f = root / f"docker-compose.{env}.yml"
        if not f.exists():
            out.append(f"{f.name}: нет файла — у проекта три compose-файла: dev, test, prod")
            continue
        svc = services(f.read_text(encoding="utf-8", errors="replace"))
        if not svc:
            out.append(f"{f.name}: не нашёл блок services — проверьте вручную")
            continue
        for name, block in svc.items():
            build = key_block(block, "build")
            if build:
                ctx = re.search(r"context:\s*([^\s#]+)", build)
                dockerfile = re.search(r"dockerfile:\s*([^\s#]+)", build)
                target = re.search(r"target:\s*([^\s#]+)", build)
                inline = build.split("\n")[0].strip()
                context = ctx.group(1) if ctx else (inline or ".")
                builds.append((context, dockerfile.group(1) if dockerfile else "Dockerfile",
                               target.group(1) if target else ""))
            if env in ("test", "prod") and build:
                if not re.search(r"^\s*true\s*$", key_block(block, "read_only"), re.M) and "true" not in key_block(block, "read_only"):
                    out.append(f"{f.name}: сервис {name} — нет read_only: true")
                if "/tmp" not in key_block(block, "tmpfs"):
                    out.append(f"{f.name}: сервис {name} — /tmp не смонтирован как tmpfs")
                if "ALL" not in key_block(block, "cap_drop"):
                    out.append(f"{f.name}: сервис {name} — нет cap_drop: [ALL]")
                if "no-new-privileges" not in key_block(block, "security_opt"):
                    out.append(f"{f.name}: сервис {name} — нет security_opt no-new-privileges")
            if env in ("test", "prod") and name == "backend" and "/health/ready" not in key_block(block, "healthcheck"):
                out.append(f"{f.name}: у backend нет healthcheck на /health/ready")
            if env == "prod" and not build:
                image = key_block(block, "image")
                if STATEFUL.search(image):
                    out.append(f"{f.name}: сервис {name} ({image.strip()}) — в prod нет локальных хранилищ, база и "
                               "хранилище внешние")
    return builds


def check_images(root: Path, builds: list, out: list) -> None:
    seen, seen_ctx = set(), set()
    for context, dockerfile, target in builds:
        ctx = (root / context).resolve()
        df = (ctx / dockerfile).resolve()
        if (df, target) in seen:
            continue
        seen.add((df, target))
        rel = df.relative_to(root.resolve()) if df.is_relative_to(root.resolve()) else df
        if not df.exists():
            out.append(f"{rel}: Dockerfile, который собирает compose, не найден")
            continue
        if not (ctx / ".dockerignore").exists() and ctx not in seen_ctx:
            seen_ctx.add(ctx)
            out.append(f"{ctx.relative_to(root.resolve()) if ctx != root.resolve() else '.'}: нет .dockerignore в "
                       "контексте сборки")
        stages = re.split(r"(?im)^FROM\s+", df.read_text(encoding="utf-8", errors="replace"))[1:]
        chosen = None
        for st in stages:
            name = re.match(r"\S+(?:\s+AS\s+(\S+))?", st, re.I)
            if target and name and name.group(1) and name.group(1).lower() == target.lower():
                chosen = st
        chosen = chosen or (stages[-1] if stages else "")
        users = re.findall(r"(?im)^USER\s+(\S+)", chosen)
        user = users[-1].split(":")[0] if users else ""
        label = f"{rel}{' → ' + target if target else ''}"
        if not user:
            out.append(f"{label}: в стадии нет USER — контейнер запустится от root")
        elif not user.isdigit():
            out.append(f"{label}: USER {user} — нужен числовой uid, чтобы рантайм проверил «не root»")
        elif user == "0":
            out.append(f"{label}: USER 0 — это root")


def check_release(root: Path, version: str | None, out: list) -> None:
    rel = root / "release"
    if not rel.is_dir():
        out.append("release/: нет папки релиза — её собирает scripts/build-images.sh")
        return
    vs = sorted((p.name for p in rel.iterdir() if p.is_dir() and re.fullmatch(r"\d+(\.\d+)*", p.name)),
                key=lambda v: [int(x) for x in v.split(".")])
    v = version or (vs[-1] if vs else None)
    folder = rel / v if v else None
    if not folder or not folder.is_dir():
        out.append(f"release/{v or '<версия>'}: нет папки")
        return
    names = {p.name for p in folder.iterdir()}
    if not any(n.endswith(".tar") for n in names):
        out.append(f"release/{v}: нет архива образов .tar")
    for need in ("DEPLOY.md", "openapi.yaml"):
        if need not in names:
            out.append(f"release/{v}: нет {need}")
    if not any(n.endswith(".env.example") for n in names):
        out.append(f"release/{v}: нет <project>.env.example")
    deploy = folder / "DEPLOY.md"
    if deploy.exists():
        cited = set(re.findall(r"`([\w.-]+\.(?:yml|yaml|tar|sh|example|json))`", deploy.read_text(encoding="utf-8")))
        for n in sorted(cited - names):
            if not (root / n).exists() or n.startswith(("docker-compose.", ".env")):
                out.append(f"release/{v}/DEPLOY.md: называет `{n}`, а в папке релиза его нет")


def main() -> None:
    args = sys.argv[1:]
    root = Path(next((a for a in args if not a.startswith("--") and Path(a).is_dir()), ".")).resolve()
    version = args[args.index("--version") + 1] if "--version" in args else None
    out: list[str] = []
    builds = check_compose(root, out)
    check_images(root, builds, out)
    check_release(root, version, out)
    for line in out:
        print("✗", line)
    print(f"deploy_check: сборок {len(set(builds))}, проблем {len(out)}")
    sys.exit(1 if out else 0)


if __name__ == "__main__":
    main()
