"""
contract-test-template.py — the OpenAPI the app builds against documentation/api/openapi.yaml.

Place this file at: tests/contract/test_openapi_contract.py (written once by repo-scaffold; `fastapi` → The
contract test). It needs PyYAML in the dev dependencies and no database: building the document runs no route.

What fails, per operation the app serves:
  - the contract has no operation with that method and path (path parameter names aside);
  - a different operationId;
  - a different set of statuses (500, 503 and `default` aside — the global handler answers them, not the route);
  - a different request body or success-response body: media types, property names, `required`, `type`,
    `nullable`, `enum`, string `format`, length / range / item bounds, `pattern`;
  - a different query or header parameter: its name, whether it is required, its schema.
What does not fail:
  - a contract operation the app does not serve yet — reported as a warning; the plan builds it;
  - descriptions, titles, examples, defaults, error-body schemas (one handler renders them all);
  - the forms two generators write differently for the same thing: 3.0 `nullable` vs 3.1 `anyOf [..., null]`,
    `$ref` vs inline, `allOf` merged, numeric `format`s, the 3.0 boolean `exclusiveMinimum`.

A red test is a route that differs from the contract: fix the route, or change the contract first
(`openapi-spec-generator`). A generator quirk that is not a contract difference is normalized in `_norm` with a
comment — never an operation added to NOT_IN_CONTRACT to make the test pass.
"""

from __future__ import annotations

import json
import re
import warnings
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import yaml
from fastapi.openapi.utils import get_openapi

# Placeholder — the app object (with an architecture document: the foundation §5 path in bootstrap/).
from src.main import app

REPO_ROOT = Path(__file__).resolve().parents[2]  # placeholder: tests/contract/ → the folder holding documentation/
CONTRACT = REPO_ROOT / "documentation" / "api" / "openapi.yaml"
# Routes the contract does not describe on purpose (health, metrics) — (method, path as the app serves it).
NOT_IN_CONTRACT = {("get", "/health")}

METHODS = ("get", "put", "post", "delete", "patch")
IGNORED_STATUSES = {"500", "503", "default"}
SKIPPED_HEADERS = {"authorization"}  # carried by the security scheme, not a parameter of the operation
COMPARED_KEYS = (
    "format", "enum", "nullable", "minLength", "maxLength", "minimum", "maximum",
    "exclusiveMinimum", "exclusiveMaximum", "minItems", "maxItems", "pattern",
)
NUMBER_FORMATS = {"int32", "int64", "float", "double"}
SAFE_INTEGER = 2**53 - 1
PATH_PARAMETER = re.compile(r"\{[^}]*\}")


class BrokenReferenceError(ValueError):
    """A `$ref` that cannot be followed: a file reference inside the app's one-dict document, or a cycle."""

    def __init__(self, ref: str) -> None:
        super().__init__(f"cannot follow $ref {ref!r}")
        self.ref = ref


class Document:
    """An OpenAPI document whose `$ref`s resolve, across files (the split contract) or inside one dict."""

    def __init__(self, root: dict[str, Any], path: Path | None = None) -> None:
        self.root = root
        self.path = path
        self._files: dict[Path, Any] = {} if path is None else {path: root}

    @classmethod
    def from_file(cls, path: Path) -> Document:
        return cls(yaml.safe_load(path.read_text(encoding="utf-8")), path.resolve())

    def _file(self, path: Path) -> Any:
        if path not in self._files:
            self._files[path] = yaml.safe_load(path.read_text(encoding="utf-8"))
        return self._files[path]

    def resolve(self, node: Any, base: Path | None) -> tuple[Any, Path | None]:
        for _ in range(50):
            if not (isinstance(node, dict) and isinstance(node.get("$ref"), str)):
                return node, base
            ref: str = node["$ref"]
            file_part, _, fragment = ref.partition("#")
            if file_part and base is None:
                raise BrokenReferenceError(ref)
            if file_part and base is not None:
                base = (base.parent / file_part).resolve()
            node = self.root if base is None else self._file(base)
            for part in (p for p in fragment.split("/") if p):
                node = node[part.replace("~1", "/").replace("~0", "~")]
        raise BrokenReferenceError(str(node.get("$ref", "")))  # still a $ref after 50 hops: a cycle


@dataclass(frozen=True)
class Where:
    doc: Document
    base: Path | None
    depth: int = 0

    def deeper(self) -> Where:
        return Where(self.doc, self.base, self.depth + 1)


def _merge_all_of(node: dict[str, Any], at: Where, out: dict[str, Any]) -> None:
    """allOf: the parts merged into one object."""
    for part in node.get("allOf", []):
        merged = _norm(part, at.deeper())
        out.setdefault("properties", {}).update(merged.pop("properties", {}))
        out["required"] = sorted(set(out.get("required", [])) | set(merged.pop("required", [])))
        for key, value in merged.items():
            out.setdefault(key, value)


def _fold_nullable(node: dict[str, Any], at: Where, out: dict[str, Any]) -> None:
    """3.1 nullable: anyOf [X, {type: null}] → X with nullable; type: [string, "null"] → string with nullable."""
    for union in ("anyOf", "oneOf"):
        members = [at.doc.resolve(m, at.base)[0] for m in node.get(union, [])]
        rest = [m for m in members if m != {"type": "null"}]
        if not members:
            continue
        if len(rest) == 1:
            out.update(_norm(rest[0], at.deeper()))
        else:
            out[union] = sorted(json.dumps(_norm(m, at.deeper()), sort_keys=True) for m in rest)
        if len(rest) < len(members):
            out["nullable"] = True
    kind = node.get("type")
    if isinstance(kind, list):
        if "null" in kind:
            out["nullable"] = True
        kinds = sorted(str(k) for k in kind if k != "null")
        out["type"] = kinds[0] if len(kinds) == 1 else kinds
    elif kind is not None:
        out["type"] = kind


def _tidy(out: dict[str, Any]) -> None:
    """One form for what generators write differently: bounds, numeric formats, safe-integer bounds."""
    if isinstance(out.get("enum"), list):
        out["enum"] = sorted(out["enum"], key=json.dumps)
    for flag, bound in (("exclusiveMinimum", "minimum"), ("exclusiveMaximum", "maximum")):
        if out.get(flag) is True:  # 3.0 boolean form → the 3.1 number form
            out[flag] = out.pop(bound, None)
        if out.get(flag) is False:
            del out[flag]
    if out.get("format") in NUMBER_FORMATS:
        del out["format"]
    if out.get("minimum") == -SAFE_INTEGER:
        del out["minimum"]
    if out.get("maximum") == SAFE_INTEGER:
        del out["maximum"]
    if out.get("nullable") is False:
        del out["nullable"]


def _norm(raw: Any, at: Where) -> dict[str, Any]:
    """The parts of a schema the contract fixes, in one form whichever generator wrote it."""
    node, base = at.doc.resolve(raw, at.base)
    if not isinstance(node, dict) or at.depth > 25:
        return {}
    at = Where(at.doc, base, at.depth)
    out: dict[str, Any] = {}
    _merge_all_of(node, at, out)
    _fold_nullable(node, at, out)
    out.update({key: node[key] for key in COMPARED_KEYS if key in node})
    if "const" in node:
        out["enum"] = [node["const"]]
    _tidy(out)
    for name, prop in node.get("properties", {}).items():
        out.setdefault("properties", {})[name] = _norm(prop, at.deeper())
    if "required" in node:
        out["required"] = sorted(set(out.get("required", [])) | set(node["required"]))
    if "items" in node:
        out["items"] = _norm(node["items"], at.deeper())
    return out


def _diff(where: str, contract: Any, served: Any, found: list[str]) -> None:
    if isinstance(contract, dict) and isinstance(served, dict):
        keys = set(contract) | set(served)
        if "format" in served and "pattern" in served and "pattern" not in contract:
            keys.discard("pattern")  # a generator's own regex for a string format
        for key in sorted(keys):
            _diff(f"{where}.{key}", contract.get(key), served.get(key), found)
    elif contract != served:
        found.append(f"{where}: contract {json.dumps(contract)}, app {json.dumps(served)}")


def _route_key(method: str, path: str) -> str:
    """`GET /bookings/{}` — path parameter names differ between the contract and the code."""
    return method.upper() + " " + PATH_PARAMETER.sub("{}", path)


@dataclass(frozen=True)
class Operation:
    doc: Document
    path: str
    op: dict[str, Any]
    base: Path | None

    def parameters(self) -> dict[str, Any]:
        params: dict[str, Any] = {}
        position = 0
        for raw in self.op.get("parameters", []):
            param, base = self.doc.resolve(raw, self.base)
            where = param["in"]
            if where == "cookie" or (where == "header" and param["name"].lower() in SKIPPED_HEADERS):
                continue
            schema = _norm(param.get("schema", {}), Where(self.doc, base))
            schema.pop("nullable", None)  # a query string has no null: `str | None = None` is just not required
            key = f"path#{position}" if where == "path" else f"{where}:{param['name']}"
            if where == "path":
                position += 1
            params[key] = {"required": bool(param.get("required", False)), "schema": schema}
        return params

    def bodies(self, holder: Any) -> dict[str, Any]:
        holder, base = self.doc.resolve(holder, self.base)
        content = holder.get("content", {}) if isinstance(holder, dict) else {}
        return {media: _norm(spec.get("schema", {}), Where(self.doc, base)) for media, spec in content.items()}

    def response(self, code: str) -> Any:
        responses = self.op.get("responses", {})
        return responses.get(code, responses.get(int(code)) if code.isdigit() else None)

    def statuses(self) -> list[str]:
        return sorted(set(map(str, self.op.get("responses", {}))) - IGNORED_STATUSES)


def _operations(doc: Document, prefix: str = "") -> dict[str, Operation]:
    found: dict[str, Operation] = {}
    for path, raw_item in doc.root.get("paths", {}).items():
        item, base = doc.resolve(raw_item, doc.path)
        served_path = path[len(prefix):] if prefix and path.startswith(prefix) else path
        for method in METHODS:
            if method in item:
                found[_route_key(method, served_path)] = Operation(doc, served_path, item[method], base)
    return found


def _compare(key: str, c: Operation, s: Operation, found: list[str]) -> None:
    if c.op.get("operationId") != s.op.get("operationId"):
        found.append(f"{key}: operationId contract {c.op.get('operationId')!r}, app {s.op.get('operationId')!r}")
    name = f"{key} ({c.op.get('operationId')})"
    _diff(f"{name} parameters", c.parameters(), s.parameters(), found)
    _diff(f"{name} request body", c.bodies(c.op.get("requestBody", {})), s.bodies(s.op.get("requestBody", {})), found)
    c_codes, s_codes = c.statuses(), s.statuses()
    if c_codes != s_codes:
        found.append(f"{name}: statuses contract {c_codes}, app {s_codes}")
    for code in (x for x in c_codes if x.startswith("2") and x in s_codes):
        _diff(f"{name} response {code}", c.bodies(c.response(code)), s.bodies(s.response(code)), found)


def _documents() -> tuple[Document, Document, str]:
    contract = Document.from_file(CONTRACT)
    servers = contract.root.get("servers") or [{}]
    prefix = urlparse(servers[0].get("url", "")).path.rstrip("/")
    # Built from the routes, not app.openapi(): an app that serves the contract file itself overrides that one.
    served = Document(get_openapi(title="contract test", version="0", routes=app.routes))
    return contract, served, prefix


def test_every_served_operation_matches_the_contract() -> None:
    contract, served, prefix = _documents()
    expected = _operations(contract)
    actual = _operations(served, prefix)
    found: list[str] = []
    for key, s in sorted(actual.items()):
        if (key.split(" ")[0].lower(), s.path) in NOT_IN_CONTRACT:
            continue
        if key not in expected:
            found.append(f"{key}: the app serves it, the contract has no such operation")
            continue
        _compare(key, expected[key], s, found)
    pending = sorted(set(expected) - set(actual))
    if pending:
        warnings.warn(f"contract operations not served yet: {pending}", stacklevel=1)
    assert not found, "the app differs from documentation/api/openapi.yaml:\n" + "\n".join(found)
