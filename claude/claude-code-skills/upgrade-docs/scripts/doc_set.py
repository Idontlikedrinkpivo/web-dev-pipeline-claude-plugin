"""The plugin's document set for a project: which documents its code calls for, which it has, which are missing.

Used by project_format.py `set`. A project written without the plugin has its own documents or none; the format
changes in changes.json apply only to documents the plugin wrote, so «nothing pending» there says nothing about
whether the set exists. This module says that: a document is needed when the code shows the thing it describes
(a database, an HTTP API, screens, containers), present when its canonical file is there.
"""
from __future__ import annotations

import re
from pathlib import Path

SERVER = r'"(fastify|express|koa|hono|@nestjs/core|@hapi/hapi)"'
SERVER_PY = r"\b(fastapi|flask|django|starlette|litestar|aiohttp)\b"
DB = r'"(pg|postgres|mysql2|better-sqlite3|sqlite3|@prisma/client|prisma|drizzle-orm|typeorm|knex|sequelize|mongoose|kysely|mssql|oracledb)"'
DB_PY = r"\b(sqlalchemy|sqlmodel|psycopg|psycopg2|asyncpg|aiosqlite|peewee|tortoise-orm|pymongo|motor|django)\b"
UI = r'"(react|vue|svelte|@angular/core|next|nuxt|solid-js|preact)"'
NODE = ["package.json", "*/package.json", "*/*/package.json"]  # a monorepo's apps/api, packages/domain
PY = ["pyproject.toml", "*/pyproject.toml", "*/*/pyproject.toml", "requirements.txt", "*/requirements.txt"]
SKIP = {"node_modules", ".venv", "venv", ".git", "dist", "build", ".next", "vendor", "site-packages"}
MIGRATIONS = ["migrations", "*/migrations", "alembic", "*/alembic", "drizzle", "*/drizzle", "prisma/schema.prisma",
              "*/prisma/schema.prisma", "db/migrations", "*/db/migrations", "documentation/db/migrations"]
DOCKER = ["Dockerfile", "*/Dockerfile", "*.Dockerfile", "*/*.Dockerfile", "docker-compose*.yml", "compose*.yml",
          "docker-compose*.yaml"]


def _files(root: Path, p: str) -> list:
    """The paths a glob names, never inside dependencies or build output (node_modules holds other projects'
    package.json files)."""
    if "*" not in p:
        return [root / p] if (root / p).exists() else []
    return [f for f in root.glob(p) if not SKIP & set(f.relative_to(root).parts)]


def _any(root: Path, paths: list) -> bool:
    return any(_files(root, p) for p in paths)


def _grep(root: Path, paths: list, pattern: str) -> bool:
    rx = re.compile(pattern)
    for p in paths:
        for f in _files(root, p):
            try:
                if f.is_file() and rx.search(f.read_text(encoding="utf-8", errors="replace")):
                    return True
            except OSError:
                continue
    return False


def signals(root: Path) -> dict:
    """What the code shows, each with the evidence a person can check."""
    code = _any(root, NODE + PY + ["go.mod", "*/go.mod", "pom.xml", "*/pom.xml", "*.csproj", "*/*.csproj"])
    server = _grep(root, NODE, SERVER) or _grep(root, PY, SERVER_PY)
    db = _grep(root, NODE, DB) or _grep(root, PY, DB_PY) or _any(root, MIGRATIONS)
    ui = _grep(root, NODE, UI)
    containers = _any(root, DOCKER)
    return {"code": code, "server": server, "db": db, "ui": ui, "containers": containers}


# chain order; each: id, title, the files that make it present, the signal that makes it needed, how it is written
SET = [
    ("set-business-requirements", "Бизнес-требования",
     ["documentation/requirements/business-requirements/business-requirements.md"], "code",
     "brainstorm, как есть: цель и границы продукта по коду и прежним документам, затем допрос (grill-me)"),
    ("set-srs", "Требования (SRS)", ["documentation/requirements/srs/srs.md"], "code",
     "srs-writer, как есть: сценарии и правила, которые код выполняет, затем допрос и ревью"),
    ("set-db-schema", "Схема базы данных", ["documentation/db/schema.md"], "db",
     "db-schema-design, как есть: по миграциям проекта (они остаются на месте), затем ревью"),
    ("set-api", "Контракт API (OpenAPI)", ["documentation/api/openapi.yaml"], "server",
     "openapi-spec-generator, как есть: каждый маршрут приложения — операция, затем ревью"),
    ("set-architecture", "Архитектура: основа, доменная модель, сценарии",
     ["documentation/architecture/architecture.md", "documentation/architecture/domain.md",
      "documentation/architecture/scenarios/*/*.md"], "code",
     "clean-architecture-design, как есть: модули, слои и сценарии, как они есть в коде, затем ревью каждого документа"),
    ("set-screen-specs", "ТЗ на экраны", ["documentation/ui/screen-specs/S-*.md|documentation/ui/*/screen-specs/S-*.md"],
     "ui", "screen-spec, как есть: экраны по маршрутам и компонентам фронтенда (кадров Figma нет), затем ревью"),
    ("set-test-cases", "Тест-кейсы", ["documentation/ui/test-cases/README.md|documentation/ui/*/test-cases/README.md"],
     "ui", "ui-test-cases, режим write: из требований и ТЗ на экраны, как обычно"),
    ("set-deploy", "Документ развёртывания", ["documentation/deploy/deploy.md"], "containers",
     "deploy-topology, только шаг 8, как есть: по Dockerfile и compose-файлам проекта (перестройка контейнеров — "
     "изменение кода devops-ready в upgrade-code)"),
    ("set-operations", "Эксплуатационный документ", ["documentation/operations/operations.md"], "server",
     "operations-doc, как обычно: он и так пишется по построенной системе"),
    ("set-project-map", "Карта проекта", ["documentation/project-map/project-map.md"], "code",
     "repo-scaffold, только §6 «Project map», по коду"),
]
WHY = {"code": "в проекте есть код", "server": "приложение отвечает по HTTP", "db": "у приложения есть база данных",
       "ui": "есть фронтенд с экранами", "containers": "есть Dockerfile или compose-файлы"}

# the plugin's own files under documentation/ — anything else there is the project's own
OWN = re.compile(r"^(requirements/(business-requirements|srs)/|requirements/[^/]+/open-questions\.md$|"
                 r"db/(schema\.md|migrations/|tables/|diagrams/|open-questions\.md|[^/]+\.dbml$)|"
                 r"api/(openapi\.yaml|paths/|components/|open-questions\.md)|"
                 r"architecture/(architecture\.md|domain\.md|scenarios/|diagrams/|open-questions\.md)|"
                 r"ui/|deploy/|operations/|project-map/|plans/|_web-docs/|\.dev-pipeline\.json$)")


def _present(root: Path, pattern: str) -> bool:
    return any(_any(root, [alt]) for alt in pattern.split("|"))


def state(root: Path, skipped: set) -> list:
    """[(id, title, status, why, how)] in chain order; status: есть | нет | неполный | не нужен | пропущен."""
    sig = signals(root)
    out = []
    for did, title, files, need, how in SET:
        have = [f for f in files if _present(root, f)]
        if not sig[need]:
            status = "есть" if have else "не нужен"
        elif did in skipped:
            status = "пропущен"
        else:
            status = "есть" if len(have) == len(files) else "неполный" if have else "нет"
        out.append((did, title, status, WHY[need], how))
    return out


def foreign(root: Path) -> list:
    """The project's own files under documentation/, outside the plugin's set (repo-relative)."""
    doc = root / "documentation"
    if not doc.is_dir():
        return []
    return sorted(p.relative_to(root).as_posix() for p in doc.rglob("*")
                  if p.is_file() and not OWN.match(p.relative_to(doc).as_posix()) and p.name != ".DS_Store")
