#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Check the container files and the release folder against deploy-topology → Before you finish — what code can
decide, so the stage closes on facts.

    python3 deploy_check.py [<project dir>] [--version <v>]

  compose     two stands: docker-compose.test.yml and docker-compose.dev.yml exist, docker-compose.prod.yml does not.
              In test, every service built from the project (`build:`) runs read_only, with /tmp as tmpfs, cap_drop
              ALL and no-new-privileges, and `backend` has a healthcheck on /health/ready. Every published port in
              both files binds loopback; only dev may bind `${DEV_BIND:-127.0.0.1}`.
  images      every Dockerfile the compose files build: the stage they build ends with a numeric USER other than 0
              and sets APP_VERSION and CI_COMMIT_SHORT_SHA; a .dockerignore in the build context hides .env*,
              compose files, Dockerfiles, .git, tests and keys, and leaves no exception for .env.example.
  nginx       a client's nginx/: no <<…>> left, no `upstream` block, /etc/nginx/conf.d in no tmpfs of an image with a
              shell (rendered into /tmp).
  code        no switched-off TLS check in the project's source; no public CDN in a client's index.html.
  env         the project's own env:check passes — deploy/prod.env.example, deploy.md's variables tables and
              .env.example equal the render of the config schema (npm run env:check, or scripts/env_doc.py
              --check); no scripts/env_files.py, no up-prod / env / env-* make target; scripts/build-images.sh
              runs env:check before its first docker call.
  release     release/<version>/ (the given version, else the newest) holds a .tar, DEPLOY.md, an .env.example,
              one openapi.yaml, build/ and scan/; every file name DEPLOY.md cites in backticks is in that folder;
              scripts/build-images.sh ends with the scan (scripts/trivy_images.py beside it) — a kit is never built
              without one.

Exit 0 — clean; 1 — a line per problem. Run at deploy-topology's close (Before you finish). A parser of the compose
shape this skill writes, not of all YAML: an unusual layout it cannot read is reported, never passed silently.
Standard library only.
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

STATEFUL = re.compile(r"\b(postgres|postgis|mysql|mariadb|mongo|redis|valkey|minio|rabbitmq|kafka|elasticsearch|"
                      r"opensearch|clickhouse|cassandra)\b", re.I)


DOCKERIGNORE = {".env": r"^\.env\s*$", ".env.*": r"^\.env\.\*", "docker-compose*": r"^docker-compose\*",
                "Dockerfile*": r"^Dockerfile\*", ".git": r"^\.git/?\s*$", "tests/": r"^(\*\*/)?tests?/?\s*$",
                "*.pem": r"^(\*\*/)?\*\.pem\s*$", "*.key": r"^(\*\*/)?\*\.key\s*$"}
TLS_OFF = re.compile(r"verify\s*=\s*False|rejectUnauthorized\s*:\s*false|NODE_TLS_REJECT_UNAUTHORIZED|ssl\s*=\s*False|"
                     r"InsecureRequestWarning|CERT_NONE")
CDN = re.compile(r"https?://(fonts\.googleapis\.com|fonts\.gstatic\.com|cdnjs\.cloudflare\.com|cdn\.jsdelivr\.net|"
                 r"unpkg\.com|ajax\.googleapis\.com|code\.jquery\.com|cdn\.tailwindcss\.com)")
SKIP_DIRS = {"node_modules", ".venv", "venv", "dist", "build", ".next", ".git", "release", "documentation", "tests",
             "test", "__pycache__", ".claude", "coverage"}


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


def published_ports(block: str) -> list[str]:
    """Each entry of a service's `ports:` — the short form as written, the long form as `host_ip:published:target`."""
    text = key_block(block, "ports")
    out, long_form = [], {}
    for line in text.splitlines():
        item = line.strip()
        short = re.match(r"^-\s*[\"']?([^\"'#]+?)[\"']?\s*(#.*)?$", item)
        field = re.match(r"^-?\s*(target|published|host_ip|protocol|mode):\s*[\"']?([^\"'#\s]*)", item)
        if field:
            if item.startswith("-") and long_form:
                out.append(f"{long_form.get('host_ip', '')}:{long_form.get('published', '')}:{long_form.get('target', '')}")
                long_form = {}
            long_form[field.group(1)] = field.group(2)
        elif short:
            out.append(short.group(1).strip())
    if long_form:
        out.append(f"{long_form.get('host_ip', '')}:{long_form.get('published', '')}:{long_form.get('target', '')}")
    return out


def loopback(port: str, stand: str) -> bool:
    if port.startswith(("127.0.0.1:", "[::1]:", "::1:")):
        return True
    return stand == "dev" and port.startswith("${DEV_BIND:-127.0.0.1}:")


def check_compose(root: Path, out: list) -> list[tuple[str, str, str]]:
    builds = []
    prod = root / "docker-compose.prod.yml"
    if prod.exists():
        out.append("docker-compose.prod.yml: прод в репозитории не запускается — стендов два (test, dev), прод "
                   "передаётся комплектом; удалите файл (env-and-config-contract.md → Where each value lives)")
    for env in ("dev", "test"):
        f = root / f"docker-compose.{env}.yml"
        if not f.exists():
            out.append(f"{f.name}: нет файла — у проекта два стенда: test и dev")
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
            for port in published_ports(block):
                if not loopback(port, env):
                    out.append(f"{f.name}: сервис {name} — порт {port} открыт не на 127.0.0.1"
                               + (" (в сеть сайт dev открывает только ${DEV_BIND:-127.0.0.1})" if env == "dev" else ""))
            if env == "test" and build:
                if not re.search(r"^\s*true\s*$", key_block(block, "read_only"), re.M) and "true" not in key_block(block, "read_only"):
                    out.append(f"{f.name}: сервис {name} — нет read_only: true")
                if "/tmp" not in key_block(block, "tmpfs"):
                    out.append(f"{f.name}: сервис {name} — /tmp не смонтирован как tmpfs")
                if "/etc/nginx/conf.d" in key_block(block, "tmpfs"):
                    out.append(f"{f.name}: сервис {name} — запись в /etc/nginx/conf.d не нужна, настройки пишутся в /tmp")
                if "ALL" not in key_block(block, "cap_drop"):
                    out.append(f"{f.name}: сервис {name} — нет cap_drop: [ALL]")
                if "no-new-privileges" not in key_block(block, "security_opt"):
                    out.append(f"{f.name}: сервис {name} — нет security_opt no-new-privileges")
            if env == "test" and name == "backend" and "/health/ready" not in key_block(block, "healthcheck"):
                out.append(f"{f.name}: у backend нет healthcheck на /health/ready")
            if re.search(r"(?:path:\s*|env_file:\s*-?\s*)\.env\.example", key_block(block, "env_file")):
                out.append(f"{f.name}: сервис {name} читает .env.example — это перечень для людей, не источник значений")
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
        if ctx not in seen_ctx:
            seen_ctx.add(ctx)
            check_dockerignore(root, ctx, out)
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
        if not re.search(r"(?im)^ENV\b.*\bAPP_VERSION=", chosen) or not re.search(r"(?im)^ENV\b.*\bCI_COMMIT_SHORT_SHA=", chosen):
            out.append(f"{label}: в образе не задана версия — ENV APP_VERSION и CI_COMMIT_SHORT_SHA из аргументов сборки")


def check_dockerignore(root: Path, ctx: Path, out: list) -> None:
    label = ctx.relative_to(root.resolve()) if ctx != root.resolve() else "."
    f = ctx / ".dockerignore"
    if not f.exists():
        out.append(f"{label}: нет .dockerignore в контексте сборки")
        return
    text = f.read_text(encoding="utf-8", errors="replace")
    for name, pattern in DOCKERIGNORE.items():
        if not re.search(pattern, text, re.M):
            out.append(f"{label}/.dockerignore: не закрывает {name} (references/images.md → .dockerignore)")
    if re.search(r"^!.*\.env", text, re.M):
        out.append(f"{label}/.dockerignore: исключение для .env* — в образ не попадает ни один такой файл")


def check_nginx(root: Path, out: list) -> None:
    for conf in [*root.glob("nginx/nginx.conf"), *root.glob("*/nginx/nginx.conf")]:
        folder = conf.parent
        rel = folder.relative_to(root)
        for f in [conf, *sorted(folder.glob("templates/*"))]:
            text = f.read_text(encoding="utf-8", errors="replace")
            if "<<" in text and re.search(r"<<[A-Z_]+>>", text):
                out.append(f"{f.relative_to(root)}: остался шаблонный параметр <<…>>")
            if re.search(r"(?m)^\s*upstream\s+\w+\s*\{", text):
                out.append(f"{f.relative_to(root)}: блок upstream ищет адрес один раз при старте — фронт упадёт без "
                           "бэкенда (assets/nginx → upstream.conf.template)")
        if not list(folder.glob("templates/*")):
            out.append(f"{rel}: нет templates/")


def check_code(root: Path, out: list) -> None:
    def walk(folder: Path):
        for item in folder.iterdir():
            if item.is_dir():
                if item.name not in SKIP_DIRS:
                    yield from walk(item)
            else:
                yield item
    for f in walk(root):
        if f.suffix in (".py", ".ts", ".tsx", ".js", ".mjs", ".cjs"):
            match = TLS_OFF.search(f.read_text(encoding="utf-8", errors="replace"))
            if match:
                out.append(f"{f.relative_to(root)}: {match.group(0)} — проверка TLS отключена; корпоративный CA "
                           "подключается файлом (env-and-config-contract.md)")
        elif f.name == "index.html":
            match = CDN.search(f.read_text(encoding="utf-8", errors="replace"))
            if match:
                out.append(f"{f.relative_to(root)}: {match.group(1)} — в закрытом контуре CDN недоступен, файл должен "
                           "лежать в образе")


def check_release(root: Path, version: str | None, out: list) -> None:
    build = root / "scripts" / "build-images.sh"
    if build.exists() and "trivy_images.py" not in build.read_text(encoding="utf-8", errors="replace"):
        out.append("scripts/build-images.sh не вызывает scripts/trivy_images.py — скан последним шагом сборки "
                   "(images.md → Hand-over, пункт 6)")
    if build.exists() and not (root / "scripts" / "trivy_images.py").exists():
        out.append("scripts/trivy_images.py: нет — скопируйте из deploy-topology/scripts/")
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
    if not list((folder / "build").glob("*Dockerfile")):
        out.append(f"release/{v}/build: нет Dockerfile образов — их копирует scripts/build-images.sh")
    if not list((folder / "scan").glob("trivy-*.json")):
        out.append(f"release/{v}/scan: нет отчётов сканера — trivy_images.py <tar> release/{v}/scan")
    if not any(n.endswith(".env.example") for n in names):
        out.append(f"release/{v}: нет <project>.env.example")
    deploy = folder / "DEPLOY.md"
    if deploy.exists():
        cited = set(re.findall(r"`([\w.-]+\.(?:yml|yaml|tar|sh|example|json))`", deploy.read_text(encoding="utf-8")))
        for n in sorted(cited - names):
            if not (root / n).exists() or n.startswith(("docker-compose.", ".env")):
                out.append(f"release/{v}/DEPLOY.md: называет `{n}`, а в папке релиза его нет")


def env_check_command(root: Path) -> tuple[list[str], Path] | None:
    """The project's env:check: the package script, or the Python generator with --check."""
    for folder, cmd in ((root / "backend", ["npm", "--prefix", "backend", "run", "--silent", "env:check"]),
                        (root, ["npm", "run", "--silent", "env:check"])):
        manifest = folder / "package.json"
        if manifest.exists():
            try:
                scripts = json.loads(manifest.read_text(encoding="utf-8")).get("scripts") or {}
            except (ValueError, AttributeError):
                scripts = {}
            if "env:check" in scripts:
                return cmd, root
    for folder in (root / "backend", root):
        if (folder / "scripts" / "env_doc.py").exists():
            runner = ["uv", "run", "python"] if shutil.which("uv") else ["python3"]
            return runner + ["scripts/env_doc.py", "--check"], folder
    return None


def check_env(root: Path, out: list) -> None:
    if (root / "scripts" / "env_files.py").exists():
        out.append("scripts/env_files.py: прежняя сборка файлов переменных — удалите; файлы собирает генератор "
                   "проекта из схемы (env-and-config-contract.md → The generator)")
    makefile = root / "Makefile"
    if makefile.exists():
        for target in re.findall(r"(?m)^(up-prod|env|env-test|env-dev|env-prod)\s*:", makefile.read_text(encoding="utf-8")):
            out.append(f"Makefile: цель {target} — стендов два, файлы переменных руками или скриптом не собираются "
                       "(compose-shape.md → Make/task-runner targets)")
    build = root / "scripts" / "build-images.sh"
    if build.exists():
        lines = [l for l in build.read_text(encoding="utf-8", errors="replace").splitlines()
                 if l.strip() and not l.lstrip().startswith("#")]
        check = next((i for i, l in enumerate(lines) if "env:check" in l or "env_doc.py" in l and "--check" in l), None)
        docker = next((i for i, l in enumerate(lines) if re.search(r"\bdocker\s", l)), None)
        if check is None or (docker is not None and docker < check):
            out.append("scripts/build-images.sh: env:check не запускается до первого docker — устаревший файл "
                       "переменных уйдёт в комплект (images.md → Hand-over, пункт 0)")
    command = env_check_command(root)
    if command is None:
        if (root / ".env.example").exists():
            out.append("нет генератора переменных (env:check) — env-and-config-contract.md → The generator")
        return
    cmd, cwd = command
    try:
        run = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=300)
    except (OSError, subprocess.TimeoutExpired) as err:
        out.append(f"env:check не запустился ({' '.join(cmd)}): {err}")
        return
    if run.returncode != 0:
        lines = [l.strip() for l in (run.stderr + run.stdout).splitlines() if l.strip()]
        out += lines[:20] or [f"env:check: код {run.returncode} ({' '.join(cmd)})"]


def main() -> None:
    args = sys.argv[1:]
    root = Path(next((a for a in args if not a.startswith("--") and Path(a).is_dir()), ".")).resolve()
    version = args[args.index("--version") + 1] if "--version" in args else None
    out: list[str] = []
    builds = check_compose(root, out)
    check_images(root, builds, out)
    check_nginx(root, out)
    check_code(root, out)
    check_release(root, version, out)
    check_env(root, out)
    for line in out:
        print("✗", line)
    print(f"deploy_check: сборок {len(set(builds))}, проблем {len(out)}")
    sys.exit(1 if out else 0)


if __name__ == "__main__":
    main()
