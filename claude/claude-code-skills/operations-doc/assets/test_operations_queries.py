"""Запросы документа эксплуатации живут вместе со схемой.

Reference test of operations-doc → references/proof.md → The query test, for a Python backend on PostgreSQL. Copy it
into the project's integration tests (beside deploy-topology's sync test) and adapt the lines marked ADAPT; nothing
else should need a change.

Without a database: every ```sql block of documentation/operations/operations.md stands under a «**З-n.**» or
«**П-n.**» heading, ids are numbered in order and every id the text names is defined, a З- block is one read-only
statement (SELECT or WITH), every table is schema-qualified, and the document cites no requirement, actor or frame id.
With the integration database: each З- query is PREPAREd and DEALLOCATEd inside a READ ONLY transaction — every table,
column and type is checked and $n inferred, nothing runs; each П- procedure runs inside a transaction that is always
rolled back (CREATE ROLE included), a psql variable (:'name') replaced by a literal. A failure names the id and the
database error, so a migration that renames a column fails the build that renames it, not the operator at night.
"""

from __future__ import annotations

import os
import re
from collections.abc import Iterator
from pathlib import Path
from typing import Any, NamedTuple

import pytest

# ADAPT: the path from this file to the repository root.
ROOT = Path(__file__).resolve().parents[2]
DOC = ROOT / "documentation" / "operations" / "operations.md"
# ADAPT: the schema the document's queries name (`<schema>.<table>`), and the one the test database uses.
DOC_SCHEMA = "app"
TEST_SCHEMA = os.environ.get("DB_SCHEMA", DOC_SCHEMA)

LABEL = re.compile(r"^\*\*([ЗП]-\d+)\.", re.M)
SQL_BLOCK = re.compile(r"^```sql[ \t]*\n(.*?)^```", re.M | re.S)
NAMED_ID = re.compile(r"(?<![\w-])([ЗП]-\d+)(?!\d)")
PSQL_VARIABLE = re.compile(r":'(\w+)'")
REQUIREMENT_ID = re.compile(r"\b(?:FR|NFR|BR|UC)-\d+|\b[AS]-\d+\b")


class Block(NamedTuple):
    label: str
    sql: str


def sql_blocks(text: str) -> list[Block]:
    """Each ```sql block with the id of the nearest «**З-n.**» / «**П-n.**» heading above it."""
    blocks = []
    for m in SQL_BLOCK.finditer(text):
        labels = LABEL.findall(text, 0, m.start())
        blocks.append(Block(labels[-1] if labels else f"без заголовка@{m.start()}", m.group(1).strip()))
    return blocks


def statements(sql: str) -> list[str]:
    """Statements of a block, split on a `;` at a line end (the document's queries hold no `;` inside a string)."""
    return [s.strip() for s in re.split(r";[ \t]*(?:\n|$)", sql) if s.strip()]


def without_comments(sql: str) -> str:
    return re.sub(r"--[^\n]*", "", sql).strip()


def unqualified_tables(sql: str) -> list[str]:
    """FROM / JOIN targets without `<DOC_SCHEMA>.`, CTE names and function calls aside."""
    ctes = {m.lower() for m in re.findall(r"(?:\bWITH|,)\s+(\w+)\s+AS\s*\(", sql, re.I)}
    out = []
    for m in re.finditer(r"\b(?:FROM|JOIN)\s+(?:LATERAL\s+)?([A-Za-z_][\w]*)(\.[A-Za-z_]\w*)?(\s*\()?", sql, re.I):
        first, rest, call = m.group(1), m.group(2), m.group(3)
        if call or first.upper() == "LATERAL":
            continue
        if (rest is None and first.lower() not in ctes) or (rest is not None and first != DOC_SCHEMA):
            out.append(m.group(0).strip())
    return out


TEXT = DOC.read_text(encoding="utf-8")
BLOCKS = sql_blocks(TEXT)
QUERIES = [b for b in BLOCKS if b.label.startswith("З-")]
PROCEDURES = [b for b in BLOCKS if b.label.startswith("П-")]


def test_document_has_queries_under_headings() -> None:
    assert QUERIES, f"{DOC}: нет ни одного блока ```sql под заголовком «**З-n.**»"
    stray = [b.label for b in BLOCKS if not b.label[:2] in ("З-", "П-")]
    assert not stray, f"{DOC}: блок ```sql без заголовка З-/П- выше: {stray}"


def test_ids_in_order_and_every_named_id_defined() -> None:
    defined = LABEL.findall(TEXT)
    for prefix in ("З-", "П-"):
        ids = [i for i in defined if i.startswith(prefix)]
        assert ids == [f"{prefix}{n}" for n in range(1, len(ids) + 1)], f"номера {prefix} по порядку: {ids}"
    missing = sorted(set(NAMED_ID.findall(TEXT)) - set(defined))
    assert not missing, f"в тексте названы, но не описаны: {missing}"


def test_document_cites_no_requirement_ids() -> None:
    assert REQUIREMENT_ID.findall(TEXT) == [], "документ эксплуатации не ссылается на FR, NFR, BR, UC, A-, S-"


@pytest.mark.parametrize("block", QUERIES, ids=lambda b: b.label)
def test_query_is_one_read_only_statement(block: Block) -> None:
    parts = statements(block.sql)
    assert len(parts) == 1, f"{block.label}: в блоке запроса должен быть один оператор"
    head = without_comments(parts[0]).split(None, 1)[0].upper()
    assert head in {"SELECT", "WITH"}, f"{block.label}: запрос начинается с SELECT или WITH, а не {head}"


@pytest.mark.parametrize("block", BLOCKS, ids=lambda b: b.label)
def test_tables_are_schema_qualified(block: Block) -> None:
    assert unqualified_tables(block.sql) == [], f"{block.label}: таблицы без схемы {DOC_SCHEMA}."


# --- against the integration database ------------------------------------------------------------------------------


@pytest.fixture
def raw_connection() -> Iterator[Any]:
    """A DB-API connection with autocommit off. ADAPT: take it from the project's engine or test fixture instead —
    with SQLAlchemy: `with engine.connect() as c: yield c.connection.driver_connection`."""
    psycopg = pytest.importorskip("psycopg")
    url = os.environ.get("TEST_DATABASE_URL")
    if not url:
        pytest.skip("TEST_DATABASE_URL не задан — запросы документа проверяются с интеграционными тестами")
    with psycopg.connect(url) as conn:
        yield conn


def for_test_schema(sql: str) -> str:
    if TEST_SCHEMA == DOC_SCHEMA:
        return sql
    return re.sub(rf'(?<![\w"]){re.escape(DOC_SCHEMA)}\.(?=[A-Za-z_"])', f'"{TEST_SCHEMA}".', sql)


@pytest.mark.parametrize("block", QUERIES, ids=lambda b: b.label)
def test_query_prepares_against_schema(block: Block, raw_connection: Any) -> None:
    sql = statements(for_test_schema(block.sql))[0]
    cur = raw_connection.cursor()
    try:
        cur.execute("SET TRANSACTION READ ONLY")  # the first statement of the driver's implicit transaction
        cur.execute(f"PREPARE operations_doc_query AS {sql}")
        cur.execute("DEALLOCATE operations_doc_query")
    except Exception as exc:  # noqa: BLE001 — the message must name the query
        pytest.fail(f"{block.label}: база отклонила запрос документа: {exc}")
    finally:
        raw_connection.rollback()


@pytest.mark.parametrize("block", PROCEDURES, ids=lambda b: b.label)
def test_procedure_runs_and_rolls_back(block: Block, raw_connection: Any) -> None:
    cur = raw_connection.cursor()
    try:
        for n, statement in enumerate(statements(PSQL_VARIABLE.sub("'operations-doc-test'", for_test_schema(block.sql))), 1):
            try:
                cur.execute(statement)
            except Exception as exc:  # noqa: BLE001
                pytest.fail(f"{block.label}, оператор {n}: база отклонила процедуру документа: {exc}")
    finally:
        raw_connection.rollback()
