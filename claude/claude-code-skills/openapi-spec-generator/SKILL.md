---
name: openapi-spec-generator
description: >-
  Generates a lintable OpenAPI 3.0 contract (documentation/api/openapi.yaml) from the SRS:
  one use case per operation, request and response schemas, problem+json
  errors, status codes, security schemes; extends an existing spec for the
  next slice. Use after `srs-writer` and `db-schema-design` when the user
  asks for OpenAPI, an API spec, endpoints, routes, or which status an error
  returns — «опиши API», «какие эндпоинты». Not for tables, screens, layers,
  Swagger 2.0, reverse-engineering controllers, or generating tests, mocks
  or SDKs.
---

# OpenAPI 3.0 Specification Generator

## Orchestrator (session)

The session writes no OpenAPI spec. The dispatched writer settles it
and nests `doc-typist` to print it. A report whose `DELEGATED` is not
`doc-typist` comes back once. The session does not dispatch the typist.

1. Stop if the SRS is missing. Name `srs-writer`. If the slice persists
   state and there is no schema document, stop and name `db-schema-design`.
   Do not wait for `clean-architecture-design`.
2. When a spec already exists, read `doc-versioning`.
   The writer runs as a subagent and cannot ask the user. Before dispatch, settle what the SRS leaves open: the auth scheme when the
   security NFR names none (no answer → root `security: []`, Step 4),
   the status of each named use-case exception the SRS gives none, and —
   on a new spec, when the SRS does not say — whether anyone outside the
   project calls the API (Step 2, Contract version).
   Ask once in chat and paste the answers into the packet's INPUTS.
3. Read `executor-catalog` and
   `executor-catalog/references/design-complexity.md`. Dispatch
   exactly one writer with
   `executor-catalog/references/design-writer-prompt.md`. Before the
   `Agent` call, write `Grade | Executor | subagent_type` for the design
   row the grade picked, then dispatch it without asking which model.
   Follow the catalog dispatch contract: `subagent_type` is the row's name
   and the call passes no `model` (the agent file holds it) unless the
   user named one. A missing agent or a rejected alias is a stop.
4. Inspect `documentation/api/openapi.yaml` on disk. Run
   `npx --yes @redocly/cli lint documentation/api/openapi.yaml` (or `spectral lint` when
   the repo already has a `.spectral.yaml`). Any `error` sends the writer
   back once with the rule ids and JSON pointers. When no linter can run
   (no Node, no network), say in the stage close that the spec was not
   linted. Do not edit the spec yourself. Escalate once on `BLOCKED` /
   `HARDER_THAN_EXPECTED` to the next design row. A second failure is a
   stop.
5. Close the stage by asking, per `pipeline` → "Asking before a
   transition". First ask about `doc-review`. Run: run it; it returns
   without asking the next stage. Skip: name it in the report. Stop:
   stop. After a run or a skip, ask the one next stage the table names. The writer does not run
   those. `doc-review` edits the body and does not bump
   `info.version`. See `doc-versioning`.

## Writer (dispatched)

You settle the contract. You do not print it. When every decision this
template needs is settled, nest `doc-typist` per `executor-catalog` →
Nesting, packet `executor-catalog/references/doc-typist-prompt.md`. A
gap this skill calls BLOCKED returns before that dispatch. Read the
file back. One correction dispatch, then the report. Do not type the
correction, and do not paste the finished spec into the typist's prompt.

Translate already-decided use cases into an HTTP contract. The algorithm
lives in the SRS use case. This skill only names the route, the
request/response schemas, and the status codes. `info.description`, operation `summary` /
`description`, and schema `description` / `example` are Russian. Do not
translate `operationId`, paths, or schema names. They say what a field or
an operation means, never how a client shows it: no «для выпадающего
списка», «показывается в модалке», colour or icon fields the SRS does not
require as data (`doc-versioning` → What, not how it looks).

## Workflow

### Step 1 — Gather Context

Read the SRS. Do not invent an endpoint that has no use case behind it.
A screen read that is not a use case is not this stage's to add; design
sends that gap back.

**The DB schema comes first when the system has storage.** `db-schema-design`
runs before this skill, and its column names and types are the contract this
spec must agree with — a schema written afterwards against an already-published
spec has to either rename columns or carry a translation layer nobody asked
for. If storage exists but no schema document does, say so and stop; the one
exception is a storage-free surface (pure computation, proxy, webhook relay),
where there is nothing to agree with.

Infer from the inputs. You cannot ask the user; a gap that needs an
answer and is not in the packet is STATUS BLOCKED with the question:

| Question | Why it matters |
|---|---|
| What does this API do? | Sets `info.title`, `info.description`, tags |
| Which use cases / queries are in scope? | One operation per use case or query |
| Authentication type(s)? | `securitySchemes`. The SRS security NFR, or the orchestrator's answer in INPUTS. What to emit — Step 4 |
| Existing partial spec to extend? | Merge rather than overwrite |

Map from the SRS and the schema:

| Source | OpenAPI |
|---|---|
| One use case | One operation (`operationId` = camelCase of that use-case verb) |
| What the use case accepts | Request body and/or path/query params |
| What the use case returns on success | Success response schema. Do not invent a body the use case did not name |
| An exception whose status the SRS names | That status. Do not re-pick 409 vs 422 |
| An exception with no status | The status in INPUTS; if none, return BLOCKED with the question. Do not pick a status in silence |
| Schema column | Property name and type. Do not rename. A closed-set column's `enum` is the code list from the schema's `## Status attributes`, verbatim |
| SRS security NFR | `securitySchemes` and root `security` (Step 4) |

If a DBML schema (`documentation/db/schema.md`) exists, every stored property in a request or
response body must exist on the corresponding table (or be a value the
use case says is computed). Flag mismatches instead of inventing a
second name.

### Step 1b — Existing spec: extend it under versioning rules

An existing `documentation/api/openapi.yaml` is the canonical contract, not a draft to
replace. Read the `doc-versioning` skill and follow it, plus what is specific
to a live HTTP contract. This invocation edits the spec in place and does
not touch `info.version` or `info.x-changelog`; the stamping commit
(`doc-versioning`) writes the number (Step 2, Contract version, says which)
and the typed rows. The report's DOWNSTREAM line names each change with
the type it implies, so the stamp can type it:

- A `description` / `summary` / `example` on an existing operation or
  property is no change — nothing to stamp. A new operation, path, schema,
  or optional property is `добавляет`. A removed or renamed `operationId`,
  path, method, schema name, or property, a property that became required,
  or a changed type, status, or error format is `ломает`. Wording of a
  cited contract sentence without a shape change is `уточняет`.
- **A breaking change follows who calls the API.** Only the project's own
  client: the `ломает` change ships in the release whose client follows it —
  front and back change together. External consumers: never a shape change
  under the same path — the change goes into a new major path beside the
  old one (Contract version). Deployed partner clients are the reason that
  rule has no exceptions.
- Reuse the existing `components/schemas` and `components/responses` instead of
  introducing a parallel name for the same concept.
- Deprecate a retired operation (`deprecated: true`) and keep it until no client
  calls it — with only the project's own client, the release where that
  client stops calling it; with external consumers, the old major's
  announced sunset. Do not delete it in the same change that replaces it.
- Do not add a row to the architecture journal, the schema journal, or the
  SRS journal because the spec changed. The report's DOWNSTREAM line also
  names the scenarios, the screen specs, generated clients, and the plan.
  Do not add a schema changelog row for an operation that changed no
  column.

### Step 2 — Build the Spec

Always produce a **complete, valid OpenAPI 3.0 spec** — never leave
placeholder comments like `# TODO: add schema`. The version is `3.0.3`,
not `3.1.0`: the Swagger Viewer preview reads only OpenAPI 3.0 and stops
on 3.1 with a blank page, while the file itself stays valid. Do not
raise the version to make a 3.1 keyword available.

`info.x-sources` is this file's `sources:` — YAML has no frontmatter, so
the pins live in `info`, next to `info.x-reviewed`. Pin the SRS and, when
the schema stage ran, the schema, each as `path@<version>` — the version
it was built from. Without them nobody can see that the API went stale
after an SRS or schema change. On an increment, move a pin only when this
pass re-read that source's new version.

**Contract version (`info.version`).** It follows who calls the API:

- **Only the project's own client** (the default): no separate number.
  `info.version` is the service version — the open iteration's version on
  a new spec (`0.1.0` on greenfield), afterwards stamped like any
  versioned document. No version in the path.
- **External consumers** — the SRS names partners or third-party systems
  that call the API, or the architecture foundation lists the Full
  trigger "versioned partner API": the contract has its own SemVer in
  `info.version`, independent of the service version (service 1.3.0 may
  bring API v2), and its major in the path (`servers: - url: /v1`). A new
  contract starts at `1.0.0` under `/v1`. A breaking change ships only as
  a new major path (`/v2`) beside the old one; the old one stays, its
  operations `deprecated: true`, until its announced sunset. An addition
  raises the contract's minor inside the current major; a fix its patch.
  `references/common-patterns.md` → Versioning Patterns shows the shape.

Either way a new spec carries the one «первый выпуск» row in
`info.x-changelog`, in the form `doc-versioning` → Changelog gives.

```yaml
openapi: "3.0.3"
info:
  title: <API Title>
  version: "0.1.0"   # the service version; a partner API has its own SemVer (Contract version)
  description: <Краткое описание на русском>
  x-sources:   # what this contract was built from, pinned by version
    - documentation/requirements/srs/srs.md@0.1.0
    - documentation/db/schema.md@0.1.0   # only when the schema stage ran
servers:
  - url: /   # relative; a host appears only when the SRS or the user named it
security: []   # the SRS named no scheme; otherwise the named scheme, declared in securitySchemes (Step 4)
tags:
  - name: <Tag>
    description: <Tag description>
paths:
  /resource:
    get:
      summary: List resources
      operationId: listResources
      tags: [<Tag>]
      parameters: []
      responses:
        "200":
          description: Success
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/ResourceList"
              example:
                items: []
                total: 0
        "401":
          $ref: "#/components/responses/Unauthorized"
        "500":
          $ref: "#/components/responses/InternalError"
components:
  schemas: {}
  responses:
    Unauthorized:
      description: Authentication required
      content:
        application/problem+json:
          schema:
            $ref: "#/components/schemas/Problem"
    InternalError:
      description: Internal server error
      content:
        application/problem+json:
          schema:
            $ref: "#/components/schemas/Problem"
  securitySchemes: {}
```

Do not emit `example.com` hosts or e-mails, and no `contact` the inputs did
not name: a placeholder host copied from this skeleton ships as the
contract.

### Step 3 — Schemas and Models

- **Always use `$ref`** for any schema used in more than one place.
- Include `example` or `examples` on every schema and response body.
- Mark required fields with the `required` array.
- Use `nullable: true` on a single `type` for a field that may be absent as JSON null. Do not use `type: [string, "null"]`: that is OpenAPI 3.1, and this spec is 3.0.
- Prefer `format` keywords: `int32`, `int64`, `float`, `date`, `date-time`, `uuid`, `email`, `uri`, `byte`, `binary`.
- **Property casing is the column casing.** A stored property is the column
  name verbatim (`snake_case`, e.g. `starts_at`). Wrapper, computed, and query
  and path parameter names use the same casing (`page_size`, `next_cursor`,
  `user_id`). Do not mix camelCase and snake_case property names in one
  spec; `operationId` stays camelCase.

**Common schema patterns:**

```yaml
# Collection page — keyset by default: query params `cursor` (opaque) and `limit`.
# Offset paging (`page`, `page_size`, `total`) only when the SRS asks for page
# numbers or a total count on screen.
ResourcePage:
  type: object
  required: [items, next_cursor]
  properties:
    items:
      type: array
      items:
        $ref: "#/components/schemas/Resource"
    next_cursor:
      type: string
      nullable: true
      description: null on the last page
      example: eyJpZCI6MTAwfQ

# Error body — RFC 9457 Problem Details, media type application/problem+json
Problem:
  type: object
  properties:
    type:
      type: string
      format: uri-reference
      default: about:blank
      example: https://errors.example.invalid/hold-limit-reached
    title:
      type: string
      example: Превышен лимит броней
    status:
      type: integer
      format: int32
      example: 409
    detail:
      type: string
    instance:
      type: string
      format: uri-reference
    code:
      type: string
      description: Имя исключения use case из SRS; VALIDATION_ERROR для 422 по полям
      example: HOLD_LIMIT_REACHED
    errors:
      type: array
      description: только у 422 VALIDATION_ERROR — каждое поле, не прошедшее схему
      items:
        type: object
        required: [field, message]
        properties:
          field: { type: string, example: starts_at }
          message: { type: string }

# Timestamps mixin (use allOf)
Timestamps:
  type: object
  properties:
    created_at:
      type: string
      format: date-time
    updated_at:
      type: string
      format: date-time
```

Every 4xx and 5xx response uses `application/problem+json` with `Problem`.
A named use-case error sets `code` to the SRS exception name and gets a
stable `type` URI; do not add a second error schema. When an existing spec
already uses another error format, keep it (Step 1b) — changing it is a
`ломает` change, not a silent migration.

### Step 4 — Security Schemes

Read `references/security-schemes.md` for the scheme the SRS named.
Quick reference:

| Scheme | OAS 3.0 type | Notes |
|---|---|---|
| Bearer JWT | `http`, scheme `bearer` | Only when the SRS named JWT |
| API Key (header) | `apiKey`, in `header` | e.g. `X-API-Key` |
| OAuth 2 | `oauth2` | Use `flows` to define grant types |
| OpenID Connect | `openIdConnect` | Provide `openIdConnectUrl` |

Apply security **globally** at the root and **override per-operation** only
where it differs (public endpoints use `security: []`).

If the SRS names no scheme, set
**root** `security: []`. Do not omit the `security` key — an omitted key is
not the same as an empty array — and do not invent Bearer JWT /
`securitySchemes` to fill the gap: a guessed scheme becomes the contract
every client implements.

Do not emit API keys in query strings, OAuth password flow, or implicit flow.

If the spec defines any `callbacks:` entry, add signature verification —
see "Webhook signature verification" in `references/common-patterns.md`. A
webhook with no verifiable sender is an open write endpoint with no auth.

### Step 5 — Parameters

**Path parameters** — always `required: true`:
```yaml
parameters:
  - name: user_id
    in: path
    required: true
    schema:
      type: string
      format: uuid
    example: 123e4567-e89b-12d3-a456-426614174000
```

**Query parameters** — document defaults and enums:
```yaml
  - name: status
    in: query
    schema:
      type: string
      enum: [active, inactive, pending]
      default: active
```

**Headers** — only when the SRS or the architecture names them, declare
`X-Request-ID` and other correlation ids as common
parameters under `components/parameters`.

### Step 6 — Response Codes

Status vocabulary — pick per operation, never copy the whole table:

| Code | When |
|---|---|
| `200` | Successful GET, PUT, PATCH |
| `201` | Successful POST that creates a resource |
| `204` | Successful DELETE (no body) |
| `400` | The request cannot be parsed at all: malformed JSON, an undecodable or tampered cursor |
| `401` | Missing or invalid auth |
| `403` | Authenticated but not authorized |
| `404` | Resource not found |
| `409` | Conflict (duplicate, state mismatch) |
| `422` | A body, query, or path field fails its schema (`code: VALIDATION_ERROR` with `errors`), or a named use-case error the SRS sets to 422 |
| `429` | Rate limited |
| `500` | Internal server error |

Per operation emit exactly: its success code; one response per named
use-case error; `422` (`VALIDATION_ERROR`) when it takes a body or
parameters; `400` only when it takes a JSON body or a cursor; `401` and
`403` only when the operation is secured; `404` only when the path names a
resource id; `429` only when the SRS names a rate limit; `500` always.
`409` appears only as a named use-case error.

**This file is the one source** for the error body, the validation status,
the casing, and the page shape. Stack skills (`typescript-fastify`,
`fastapi`, test skills) implement what `documentation/api/openapi.yaml` says and do not
define their own. A code the operation
cannot return misleads `screen-spec` and every generated client.

The status of a **named** use-case error is not chosen from the generic
4xx table: it is the SRS status or the orchestrator's answer in INPUTS
(Step 1 mapping). Do not stop to wait for an architecture table. A status label
shown to the client is the schema `label` column, not an example
invented here.

Use `$ref` to `components/responses` for `401`, `403`, `404`, `429`, `500`.

### Step 7 — Quality Checklist

Before delivering the spec, verify:

- [ ] `openapi: "3.0.3"` present, not `3.1.0`
- [ ] `info.version` per Contract version; `info.x-sources` pins each source as `path@<version>` — Step 2
- [ ] Every path has at least one operation
- [ ] Every operation has a unique camelCase `operationId` matching a use case or query — Step 1
- [ ] Every operation has exactly the codes Step 6 derives: a success code, `500`, one response per use-case failure with the Step 1 status
- [ ] Success bodies and field names match the use case and the schema's DBML — Step 1
- [ ] All `$ref` targets exist in `components/`
- [ ] `required` and at least one `example` on every body — Step 3
- [ ] Security per Step 4; every `callbacks:` entry has a signature header
- [ ] Tags defined at root level to match operation tags
- [ ] No orphaned schemas (everything in `components/schemas` is referenced)
- [ ] `redocly lint` (recommended) reports no `error`, or the close says why it could not run

### Step 8 — Output

1. `doc-typist` writes `documentation/api/openapi.yaml` (the path `doc-versioning`
   names); the orchestrator lints it.
2. The report has exactly the packet's fields. A use case left without an
   operation goes to CONCERNS; no summary table.
3. Do not run `doc-review` or `pipeline` — the orchestrator closes the stage.

Do not rewrite use-case Steps inside the spec. Do not ask to generate
test cases, mock servers, or client SDKs unless the user asks.

## Reference Files

- `references/security-schemes.md` — OpenAPI 3.0 security schemes
- `references/common-patterns.md` — Pagination, problem+json, webhooks, file upload, filtering

Read these when the SRS names auth or a listed pattern (pagination, error
bodies, webhooks, uploads) — not by default.
