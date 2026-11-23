# The env schema, generator and tests — Python (pydantic-settings)

The template of `env-and-config-contract.md` for a Python backend: the schema module, settings loading from it, the
generator `backend/scripts/env_doc.py` and the tests. The same shapes as `env-doc-typescript.md`, in
pydantic-settings terms. Copy it and replace the example entries (`MAIL_*` is a third-party mail API with a stub on
the test stand) with the project's own. `app` is the project's package; the schema sits in `bootstrap/` beside the
settings (`fastapi`) — use the folder the architecture's §5 tree gives config.

## `backend/app/bootstrap/env_schema.py`

```python
"""One description per variable: the kit file, DEPLOY.md's tables and the root .env.example are rendered from here."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final, Literal

from pydantic import AnyUrl, Field, SecretStr
from pydantic.json_schema import JsonDict
from pydantic_settings import BaseSettings, SettingsConfigDict

ENV_BLOCKS: Final = ("backend и migrate", "почта", "frontend")
BACKEND: Final = ENV_BLOCKS[0]


def env_doc(
    *, block: str, required: bool, secret: bool, prod: str, purpose: str, example: str, details: str,
    required_note: str | None = None,
) -> JsonDict:
    """The description of one variable. `prod` is the kit file's value: real, or empty / <заглушка> for a secret."""
    doc: JsonDict = {
        "block": block, "required": required, "secret": secret, "prod": prod,
        "purpose": purpose, "example": example, "details": details,
    }
    if required_note is not None:
        doc["required_note"] = required_note
    return doc


class Settings(BaseSettings):
    # A field is the variable's name in lower case (LOG_LEVEL → log_level). An empty value is unset (the default
    # applies); unknown names are ignored, so an old .local file still starts; a validation error never echoes a value.
    model_config = SettingsConfigDict(
        case_sensitive=False, env_ignore_empty=True, extra="ignore", hide_input_in_errors=True,
    )

    app_env: Literal["test", "dev", "prod"] = Field(json_schema_extra=env_doc(
        block=BACKEND, required=True, secret=False, prod="prod",
        purpose="среда приложения: test, dev или prod",
        example="`prod`", details="без неё процесс не стартует; заглушки разрешены только в test",
    ))
    log_level: Literal["debug", "info", "warning", "error", "critical"] = Field("info", json_schema_extra=env_doc(
        block=BACKEND, required=False, secret=False, prod="info",
        purpose="подробность логов: debug, info, warning, error, critical",
        example="`info`", details="значение вне списка — процесс не стартует",
    ))
    shutdown_timeout_sec: int = Field(25, ge=1, le=25, json_schema_extra=env_doc(
        block=BACKEND, required=False, secret=False, prod="25",
        purpose="сколько секунд дорабатывать запросы после SIGTERM",
        example="`25`", details="меньше 30 с grace period пода",
    ))
    database_url: SecretStr = Field(json_schema_extra=env_doc(
        block=BACKEND, required=True, secret=True,
        prod="postgresql+asyncpg://<пользователь>:<пароль>@<хост>:5432/<база>?options=-csearch_path%3D<схема>",
        purpose="подключение к PostgreSQL",
        example="`postgresql+asyncpg://user:***@host:5432/db?options=-csearch_path%3D<схема>`",
        details="у migrate — учётка-владелец схемы, у backend — учётка только для данных; у каждого контейнера своё значение",
    ))
    mail_api_url: AnyUrl = Field(json_schema_extra=env_doc(
        block="почта", required=True, secret=False, prod="<адрес почтового сервиса>",
        purpose="адрес почтового сервиса",
        example="`https://mail.example.ru/api`", details="на стенде test — заглушка mail-stub",
    ))
    mail_api_token: SecretStr | None = Field(None, json_schema_extra=env_doc(
        block="почта", required=False, secret=True, prod="",
        purpose="токен почтового сервиса; пусто — письма не отправляются",
        example="`***`", details="Bearer-токен; без него процесс работает, писем нет",
    ))
    # From the image (APP_VERSION, CI_COMMIT_SHORT_SHA), not from the operator: no env_doc, not in the kit file.
    app_version: str = "dev"
    ci_commit_short_sha: str = "unknown"


IMAGE_FIELDS: Final = frozenset({"app_version", "ci_commit_short_sha"})


@dataclass(frozen=True)
class Documented:
    name: str
    block: str
    required: bool
    secret: bool
    default: str | None
    prod: str
    purpose: str
    example: str
    details: str
    required_note: str | None = None


def schema_variables() -> list[Documented]:
    out: list[Documented] = []
    for field_name, field in Settings.model_fields.items():
        if field_name in IMAGE_FIELDS:
            continue
        name = field_name.upper()
        extra = field.json_schema_extra
        if not isinstance(extra, dict):
            raise TypeError(f"{field_name}: no env_doc(...) in json_schema_extra")
        default = None if field.is_required() or field.default is None else str(field.default)
        note = extra.get("required_note")
        out.append(Documented(
            name=name, block=str(extra["block"]), required=bool(extra["required"]), secret=bool(extra["secret"]),
            default=default, prod=str(extra["prod"]), purpose=str(extra["purpose"]),
            example=str(extra["example"]), details=str(extra["details"]),
            required_note=None if note is None else str(note),
        ))
    return out


RECOGNIZED_ENV_KEYS: Final = tuple(v.name for v in schema_variables())
# Required = `required` with no default; the start check and the tests use this one list.
REQUIRED_ENV_KEYS: Final = tuple(v.name for v in schema_variables() if v.required and v.default is None)

# The frontend image's variables (nginx): in the kit file and DEPLOY.md, never read by the backend.
FRONTEND_ENV_VARIABLES: Final = (
    Documented(
        name="BACKEND_SERVICE", block="frontend", required=True, secret=False, default=None,
        prod="<сервис backend>:8000", purpose="куда nginx проксирует /api/",
        example="`backend:8000`", details="имя сервиса backend и его порт",
    ),
    Documented(
        name="SECURE_MODE", block="frontend", required=True, secret=False, default=None, prod="plain",
        purpose="plain — HTTP на 8080; secure — TLS на самом поде", example="`plain`", details="TLS обычно у ingress",
    ),
)


@dataclass(frozen=True)
class StandVariable:
    """Read only by compose (stand infrastructure), never by the app: the root .env.example only."""

    name: str
    secret: bool
    purpose: str


STAND_ENV_VARIABLES: Final = (
    StandVariable("DEV_BIND", False, "на каком интерфейсе открыт сайт стенда dev: 127.0.0.1 или 0.0.0.0"),
    StandVariable("DEV_DB_PASSWORD", True, "пароль локальной PostgreSQL стенда dev"),
)

# What each .local file may hold — secrets and per-machine values — with the root .env.example's value.
LOCAL_ENV_FILES: Final = (
    (".env.test.local", (("MAIL_API_TOKEN", ""),)),
    (".env.dev.local", (("MAIL_API_URL", ""), ("MAIL_API_TOKEN", ""), ("DEV_BIND", "127.0.0.1"), ("DEV_DB_PASSWORD", ""))),
)
```

## Loading the settings — `backend/app/bootstrap/settings.py`

```python
from pydantic import ValidationError

from app.bootstrap.env_schema import Settings

__all__ = ["Settings", "load_settings"]


def load_settings() -> Settings:
    try:
        settings = Settings()  # type: ignore[call-arg]  # the values come from the environment
    except ValidationError as exc:
        names = ", ".join(".".join(str(part) for part in error["loc"]) for error in exc.errors())
        raise SystemExit(f"Invalid environment configuration: {names}") from None
    # Then the fail-fast rules of env-and-config-contract.md: the mock gate, the paired flags, the placeholders.
    return settings
```

## `backend/scripts/env_doc.py` — the generator

```python
#!/usr/bin/env python3
"""Renders deploy/prod.env.example, deploy.md's variables tables and the root .env.example from the schema.

uv run python scripts/env_doc.py           write the three files (env:doc)
uv run python scripts/env_doc.py --check   compare; exit 1 naming each stale file (env:check)
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
ROOT = BACKEND_DIR.parent
sys.path.insert(0, str(BACKEND_DIR))  # the app package, whether or not uv installed it

from app.bootstrap.env_schema import (  # noqa: E402
    ENV_BLOCKS, FRONTEND_ENV_VARIABLES, LOCAL_ENV_FILES, REQUIRED_ENV_KEYS, STAND_ENV_VARIABLES, Documented,
    schema_variables,
)

SCHEMA = "backend/app/bootstrap/env_schema.py"
ENV_FILE = "deploy/prod.env.example"
DEPLOY_DOC = "documentation/deploy/deploy.md"
LOCAL_EXAMPLE = ".env.example"
DOC_TABLES: dict[str, tuple[str, ...]] = {"backend": ("backend и migrate", "почта"), "frontend": ("frontend",)}


def documented_variables() -> list[Documented]:
    return [*schema_variables(), *FRONTEND_ENV_VARIABLES]


def _markers(required: bool, secret: bool) -> str:
    return ("[required] " if required else "") + ("[secret] " if secret else "")


def _is_required(v: Documented) -> bool:
    return v.required and v.default is None


def render_env_file(variables: list[Documented] | None = None) -> str:
    variables = documented_variables() if variables is None else variables
    blocks = []
    for block in ENV_BLOCKS:
        pairs = [f"# {_markers(_is_required(v), v.secret)}{v.purpose}\n{v.name}={v.prod}" for v in variables if v.block == block]
        blocks.append("\n\n".join([f"# ===== {block} =====", *pairs]))
    return "\n\n".join(blocks) + "\n"


def _local_doc(name: str) -> tuple[bool, bool, str]:
    for stand in STAND_ENV_VARIABLES:
        if stand.name == name:
            return False, stand.secret, stand.purpose
    for v in schema_variables():
        if v.name == name:
            return name in REQUIRED_ENV_KEYS, v.secret, v.purpose
    raise ValueError(f"env-doc: {name} of {LOCAL_EXAMPLE} is neither in the schema nor in STAND_ENV_VARIABLES")


def render_local_example() -> str:
    blocks = []
    for file, keys in LOCAL_ENV_FILES:
        pairs = []
        for name, value in keys:
            required, secret, purpose = _local_doc(name)
            pairs.append(f"# {_markers(required, secret)}{purpose}\n{name}={value}")
        blocks.append("\n\n".join([f"# ===== {file} =====", *pairs]))
    return "\n\n".join(blocks) + "\n"


def render_table(blocks: tuple[str, ...], variables: list[Documented] | None = None) -> str:
    variables = documented_variables() if variables is None else variables
    rows = [
        f"| {v.name} | {v.required_note or ('да' if _is_required(v) else 'нет')} | {'да' if v.secret else 'нет'} "
        f"| {v.example} | {v.details} |"
        for v in variables if v.block in blocks
    ]
    return "\n".join(["| Переменная | Обязательна | Секрет | Пример / формат | Что задаёт |", "|---|---|---|---|---|", *rows])


def _open(table: str) -> str:
    return f"<!-- env-doc:{table} — сгенерировано из {SCHEMA} (uv run python scripts/env_doc.py в backend/), руками не править -->"


def render_deploy_doc(doc: str, variables: list[Documented] | None = None) -> str:
    for table, blocks in DOC_TABLES.items():
        pair = re.compile(rf"<!-- env-doc:{table}[^>]*-->.*?<!-- /env-doc:{table} -->", re.S)
        if not pair.search(doc):
            raise ValueError(f"env-doc: {DEPLOY_DOC} has no <!-- env-doc:{table} … --> … <!-- /env-doc:{table} --> pair")
        body = f"{_open(table)}\n{render_table(blocks, variables)}\n<!-- /env-doc:{table} -->"
        doc = pair.sub(lambda _match: body, doc, count=1)
    return doc


def _rendered(root: Path) -> dict[str, str]:
    return {
        ENV_FILE: render_env_file(),
        DEPLOY_DOC: render_deploy_doc((root / DEPLOY_DOC).read_text(encoding="utf-8")),
        LOCAL_EXAMPLE: render_local_example(),
    }


def stale_files(root: Path = ROOT) -> list[str]:
    """The generated files that differ from their render."""
    return [file for file, text in _rendered(root).items() if (root / file).read_text(encoding="utf-8") != text]


def main(argv: list[str]) -> int:
    if "--check" in argv:
        stale = stale_files()
        for file in stale:
            print(f"env-doc: {file} differs from {Path(SCHEMA).name}; run uv run python scripts/env_doc.py in backend/", file=sys.stderr)
        return 1 if stale else 0
    for file, text in _rendered(ROOT).items():
        (ROOT / file).write_text(text, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
```

ruff's and mypy's paths name `scripts/`; pytest gets `pythonpath = ["."]` so the tests import `scripts.env_doc`.

## `backend/tests/deploy/test_env_doc.py`

```python
from __future__ import annotations

import os
import re
import shutil
import stat
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

from app.bootstrap.env_schema import (
    ENV_BLOCKS, LOCAL_ENV_FILES, RECOGNIZED_ENV_KEYS, REQUIRED_ENV_KEYS, STAND_ENV_VARIABLES, Settings,
)
from scripts.env_doc import (
    DEPLOY_DOC, ENV_FILE, LOCAL_EXAMPLE, documented_variables, render_deploy_doc, render_env_file,
    render_local_example, stale_files,
)

ROOT = Path(__file__).resolve().parents[3]
NAME_LINE = re.compile(r"^[A-Z][A-Z0-9_]*=")
STANDS = {"test": "docker-compose.test.yml", "dev": "docker-compose.dev.yml"}


def read(name: str) -> str:
    return (ROOT / name).read_text(encoding="utf-8")


def assert_layout(text: str) -> None:
    assert "\n\n\n" not in text
    assert text.endswith("\n") and not text.endswith("\n\n")
    lines = text.split("\n")
    for i, line in enumerate(lines):
        if line.startswith("# ====="):
            assert lines[i + 1] == ""
        if NAME_LINE.match(line):
            assert re.match(r"^# (?:\[required\] )?(?:\[secret\] )?\S", lines[i - 1]), line
            assert lines[i - 2] == "", line


# --- drift ---------------------------------------------------------------------------------------------------------

def test_the_committed_files_are_the_render() -> None:
    assert stale_files(ROOT) == []


def test_a_hand_edit_names_that_file_alone(tmp_path: Path) -> None:
    for file in (ENV_FILE, DEPLOY_DOC, LOCAL_EXAMPLE):
        (tmp_path / file).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(ROOT / file, tmp_path / file)
    assert stale_files(tmp_path) == []
    for file in (ENV_FILE, DEPLOY_DOC, LOCAL_EXAMPLE):
        # inside deploy.md only the tables are generated; the text around them is the author's
        edited = read(file).replace("| Переменная |", "| Имя |", 1) if file == DEPLOY_DOC else read(file) + "# hand edit\n"
        (tmp_path / file).write_text(edited, encoding="utf-8")
        assert stale_files(tmp_path) == [file]
        shutil.copy(ROOT / file, tmp_path / file)


def test_env_check_exits_0_here() -> None:
    run = subprocess.run([sys.executable, "scripts/env_doc.py", "--check"], cwd=ROOT / "backend", capture_output=True, text=True)
    assert run.returncode == 0, run.stderr


def test_render_deploy_doc_keeps_the_text_around_and_refuses_a_missing_pair() -> None:
    doc = "до\n<!-- env-doc:backend старое -->\n| x |\n<!-- /env-doc:backend -->\nмежду\n<!-- env-doc:frontend -->\n<!-- /env-doc:frontend -->\nпосле\n"
    out = render_deploy_doc(doc)
    assert out.startswith("до\n<!-- env-doc:backend ")
    assert "<!-- /env-doc:backend -->\nмежду\n" in out
    assert out.endswith("<!-- /env-doc:frontend -->\nпосле\n")
    assert render_deploy_doc(out) == out
    with pytest.raises(ValueError, match="env-doc:frontend"):
        render_deploy_doc("<!-- env-doc:backend -->\n<!-- /env-doc:backend -->\n")


# --- layout --------------------------------------------------------------------------------------------------------

def test_the_kit_file_layout() -> None:
    text = render_env_file()
    assert_layout(text)
    assert [line for line in text.split("\n") if line.startswith("# =====")] == [f"# ===== {b} =====" for b in ENV_BLOCKS]
    names = [line.split("=", 1)[0] for line in text.split("\n") if NAME_LINE.match(line)]
    assert names == [v.name for v in documented_variables()]


def test_the_local_example_layout() -> None:
    text = render_local_example()
    assert_layout(text)
    assert [line for line in text.split("\n") if line.startswith("# =====")] == [f"# ===== {f} =====" for f, _ in LOCAL_ENV_FILES]
    assert not re.search(r"<[^>]+>", text)
    assert read(LOCAL_EXAMPLE) == text


# --- schema entries ------------------------------------------------------------------------------------------------

def test_entries_have_one_name_a_one_line_purpose_and_table_cells() -> None:
    variables = documented_variables()
    assert len({v.name for v in variables}) == len(variables)
    for v in variables:
        assert re.fullmatch(r"\S[^\n]*", v.purpose), v.name
        assert v.example and v.details, v.name
        assert "|" not in v.example + v.details, v.name


def test_required_is_the_schemas_own_answer() -> None:
    for field_name, field in Settings.model_fields.items():
        assert field.is_required() == (field_name.upper() in REQUIRED_ENV_KEYS), field_name


def test_each_default_passes_its_parser(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in RECOGNIZED_ENV_KEYS:
        monkeypatch.delenv(name, raising=False)
    for name in REQUIRED_ENV_KEYS:  # any value the parser takes; only the defaults are under test
        monkeypatch.setenv(name, {"APP_ENV": "test"}.get(name, "postgresql://u:p@h:5432/d" if "URL" in name else "x"))
    Settings()  # type: ignore[call-arg]


def test_every_local_key_is_known() -> None:
    known = set(RECOGNIZED_ENV_KEYS) | {v.name for v in STAND_ENV_VARIABLES}
    for _file, keys in LOCAL_ENV_FILES:
        for name, _value in keys:
            assert name in known, name


# --- compose contract ----------------------------------------------------------------------------------------------

def environment(file: str) -> dict[str, str]:
    compose = yaml.safe_load(read(file))
    env: dict[str, str] = {}
    for service in compose["services"].values():
        for key, value in (service.get("environment") or {}).items():
            env[key] = str(value)
    return env


def test_the_local_example_lists_exactly_the_local_keys() -> None:
    keys = re.findall(r"^([A-Z][A-Z0-9_]*)=", read(LOCAL_EXAMPLE), re.M)
    assert sorted(set(keys)) == sorted({name for _f, k in LOCAL_ENV_FILES for name, _v in k})


def test_no_value_compose_fixes_is_repeated_in_the_local_file() -> None:
    for stand, file in STANDS.items():
        env = environment(file)
        local = next(k for f, k in LOCAL_ENV_FILES if f == f".env.{stand}.local")
        for name, _value in local:
            if name in env:
                assert f"${{{name}" in env[name], f"{file}: {name} is fixed in environment: and listed for .env.{stand}.local"


def test_each_kit_secret_is_empty_or_a_placeholder() -> None:
    kit = read(ENV_FILE)
    for v in documented_variables():
        if not v.secret:
            continue
        match = re.search(rf"^{v.name}=(.*)$", kit, re.M)
        assert match, v.name
        assert match[1] == "" or re.search(r"<[^>]+>", match[1]), v.name


def test_two_stands_and_no_prod_in_the_repository() -> None:
    assert not (ROOT / "docker-compose.prod.yml").exists()
    assert not re.search(r"^(up-prod|env-test|env-dev|env-prod|env):", read("Makefile"), re.M)
    for file in ("Makefile", *STANDS.values(), LOCAL_EXAMPLE, "scripts/build-images.sh"):
        assert not re.search(r"\.env\.prod(\.migrate)?\.local|docker-compose\.prod|env_files\.py", read(file)), file
    for file in STANDS.values():
        assert not re.search(r"(?:path:\s*|env_file:\s*)\.env\.example", read(file)), file


# --- make ----------------------------------------------------------------------------------------------------------

def stub(path: Path, body: str) -> None:
    path.write_text("#!/bin/sh\n" + body, encoding="utf-8")
    path.chmod(path.stat().st_mode | stat.S_IXUSR)


def test_build_images_with_a_failing_env_check_stops_before_docker(tmp_path: Path) -> None:
    for file in ("Makefile", "scripts/build-images.sh", ENV_FILE):
        (tmp_path / file).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(ROOT / file, tmp_path / file)
    (tmp_path / "backend").mkdir()
    (tmp_path / "bin").mkdir()
    stub(tmp_path / "bin/docker", 'echo "$*" >> "$CALLS"\n')
    stub(tmp_path / "bin/uv", 'echo "env-doc: deploy/prod.env.example differs" >&2\nexit 1\n')
    env = {**os.environ, "CALLS": str(tmp_path / "docker-calls"), "PATH": f"{tmp_path / 'bin'}{os.pathsep}{os.environ['PATH']}"}
    run = subprocess.run(["make", "build-images"], cwd=tmp_path, env=env, capture_output=True, text=True)
    assert run.returncode != 0
    assert ENV_FILE in run.stdout + run.stderr
    assert not (tmp_path / "docker-calls").exists()
    assert not (tmp_path / "release").exists()


def test_make_creates_an_empty_private_env_test_local_and_keeps_one(tmp_path: Path) -> None:
    shutil.copy(ROOT / "Makefile", tmp_path / "Makefile")
    assert subprocess.run(["make", ".env.test.local"], cwd=tmp_path).returncode == 0
    file = tmp_path / ".env.test.local"
    assert file.read_text() == ""
    assert file.stat().st_mode & 0o777 == 0o600
    file.write_text("MAIL_API_TOKEN=synthetic\n")
    assert subprocess.run(["make", ".env.test.local"], cwd=tmp_path).returncode == 0
    assert file.read_text() == "MAIL_API_TOKEN=synthetic\n"


def test_up_dev_without_env_dev_local_stops_naming_it(tmp_path: Path) -> None:
    shutil.copy(ROOT / "Makefile", tmp_path / "Makefile")
    run = subprocess.run(["make", "up-dev"], cwd=tmp_path, capture_output=True, text=True)
    assert run.returncode != 0
    assert ".env.dev.local" in run.stderr
    assert not (tmp_path / ".env.dev.local").exists()
```

`pyyaml` and `types-PyYAML` are dev dependencies. The old env-files test, when the project has one, is deleted in
the same commit.

## `scripts/build-images.sh` — the lines that matter

```sh
set -eu
root=$(cd "$(dirname "$0")/.." && pwd)
cd "$root"
# deploy/prod.env.example and deploy.md's variables tables are rendered from the schema; a stale one stops the build
# before Docker (needs `uv sync` in backend/).
(cd backend && uv run python scripts/env_doc.py --check)
# … the images, the tar …
cp deploy/prod.env.example "$out_dir/${project}.env.example"
```

The Makefile's stand targets are `compose-shape.md` → Make/task-runner targets.
