---
name: openapi-spec-generator
description: >-
  Writes the OpenAPI 3.0 contract from the SRS: operations, schemas, problem+json errors, security. Use for «опиши
  API», «какие эндпоинты нужны», «спецификация API». Endpoint code: work.
---

# OpenAPI 3.0 Specification Generator

## Orchestrator (session)

The session writes no OpenAPI spec. The dispatched writer settles it
and nests `doc-typist` to print it. A report whose `DELEGATED` is not
`doc-typist` comes back until it is. The session dispatches the typist
only for a print defect (step 4).

1. Stop if the SRS is missing. Name `srs-writer`. If the slice persists
   state and there is no schema document, stop and name `db-schema-design`.
   Do not wait for `clean-architecture-design`. From `upgrade-docs`
   (`MODE as-is`, `upgrade-docs/references/as-is.md`) the routes stand in
   for a missing SRS or schema: every route the app serves is an operation,
   and none of the questions below is asked — the code answers them.
2. When a spec already exists, read `doc-versioning`.
   The writer runs as a subagent and cannot ask the user. Before dispatch, settle what the SRS leaves open: the auth scheme when the
   security NFR names none (no answer → root `security: []`, Step 4),
   the status of each named use-case exception the SRS gives none, and —
   on a new spec, when the SRS does not say — whether anyone outside the
   project calls the API (Step 2, Contract version).
   One question per message (`pipeline/references/question-format.md`);
   each answer goes into the packet's ANSWERS.
   A single-file spec is split here, before dispatch (writers and the
   typist do not commit): run
   `python3 "${CLAUDE_SKILL_DIR}/scripts/split_spec.py" .` — it splits with
   redocly into the layout of Step 8, bundles the old file and the new
   root, and moves the files in only when the two bundles match, since the
   split must change no operation, schema, version or changelog row. Exit
   0: commit the move on its own («docs: OpenAPI разложен по файлам»); it is
   a move, not a version event, and the change that follows is committed by
   the stamp when the stage closes. Exit 1: the bundles differ — show the
   lines it printed and stop. Exit 3 (no Node or network): split by hand
   into the same layout — each path item and each component moved into its
   file and replaced in the root by its `$ref`, nothing else touched — say
   in the close that the bundle comparison did not run, and commit the same
   way.
3. Read `executor-catalog` and
   `executor-catalog/references/design-complexity.md`. Dispatch
   exactly one writer with
   `executor-catalog/references/design-writer-prompt.md`. Before the
   `Agent` call, write `Grade | Executor | subagent_type` for the design
   row the grade picked, then dispatch it without asking which model.
   Follow the catalog dispatch contract: `subagent_type` is `dev-pipeline:<row>`
   and the call passes no `model` (the agent file holds it) unless the
   user named one. A missing agent or a rejected alias is a stop.
4. Inspect `documentation/api/openapi.yaml` on disk. Run
   `npx --yes @redocly/cli lint documentation/api/openapi.yaml` (or `spectral lint` when
   the repo already has a `.spectral.yaml`), until the lint is clean. An
   `error` whose fix you can state as a finished line (a missing
   `description`, a broken `$ref` path, a stray key) is a print defect:
   `doc-typist` `MODE revise`, one `SETTLEMENT` line per error with its
   JSON pointer (`executor-catalog` → Nesting). An error whose fix needs a
   decision (a missing response, a schema shape) sends the writer back
   with the rule ids and pointers. When no linter can run
   (no Node, no network), say in the stage close that the spec was not
   linted. Do not edit the spec yourself. A `BLOCKED` with a question for
   the user is asked and sent back to the same row; any other `BLOCKED` /
   `HARDER_THAN_EXPECTED` escalates one design row (`executor-catalog` →
   Escalation); every round goes on while it makes progress (`pipeline` →
   `references/convergence.md`).
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

`MODE as-is` (`upgrade-docs/references/as-is.md` §5): paths, statuses and error bodies come from the code; Step 3's
problem+json rule, Step 6's status list and `references/base-schemas.md` do not apply.

Translate already-decided use cases into an HTTP contract. The algorithm
lives in the SRS use case. This skill only names the route, the
request/response schemas, and the status codes. `info.description`, operation `summary` /
`description`, and schema `description` / `example` are Russian. Do not
translate `operationId`, paths, or schema names. A description is written
for the one who calls the API — what the operation does, who may call it, what to send, what comes back, each
fact once, in plain sentences; why an error comes lives in that response; how the server does it lives in the
architecture: `references/descriptions.md`. They say what a field or
an operation means, never how a client shows it: no «для выпадающего
списка», «показывается в модалке», colour or icon fields the SRS does not
require as data (`doc-versioning` → `references/writing-rules.md` → What, not how it looks).

## Workflow

### Step 1 — Gather Context

Read the SRS. Do not invent an endpoint that has no use case behind it.
A screen read that is not a use case is not this stage's to add; design
sends that gap back.

**The DB schema comes first when the system has storage.** `db-schema-design`
runs before this skill, and its column names and types are the contract this
spec must agree with — a schema written afterwards against an already-published
spec has to either rename columns or carry a translation layer nobody asked
for. If storage exists but no schema document does, return `STATUS BLOCKED`
naming `db-schema-design`; the one
exception is a storage-free surface (pure computation, proxy, webhook relay),
where there is nothing to agree with.

Infer from the inputs. You cannot ask the user; a gap that needs an
answer and is not in the packet is STATUS BLOCKED with the question:

| Question | Why it matters |
|---|---|
| Which use cases / queries are in scope? | One operation per use case or query |
| Authentication type(s)? | `securitySchemes`. The SRS security NFR, or the answer in ANSWERS. What to emit — Step 4 |
| Existing partial spec to extend? | Merge rather than overwrite |

Map from the SRS and the schema:

| Source | OpenAPI |
|---|---|
| One use case | One operation (`operationId` = camelCase of that use-case verb) |
| What the use case accepts | Request body and/or path/query params |
| What the use case returns on success | Success response schema. Do not invent a body the use case did not name |
| An exception whose status the SRS names | That status. Do not re-pick 409 vs 422 |
| An exception with no status | The status in ANSWERS; if none, return BLOCKED with the question. Do not pick a status in silence |
| Schema column | Property name and type. Do not rename — except the keys, by the schema's rule (`db-schema-design` → How the API names keys): `public_id` is the resource's `id`, a reference `<thing>_id` keeps its name and carries the referenced row's `public_id` (uuid), a path parameter is `<resource>_id`; the internal `bigint` key never appears. A closed-set column's `enum` is the code list from the schema's `## Закрытые наборы значений`, verbatim |
| SRS security NFR | `securitySchemes` and root `security` (Step 4) |

If a DBML schema (`documentation/db/schema.md`) exists, every stored property in a request or
response body must exist on the corresponding table (or be a value the
use case says is computed). Flag mismatches instead of inventing a
second name.

### Step 1b — Existing spec: extend it under versioning rules

The spec arrives split into files (Step 8 → Layout): the session splits a
single-file spec and commits the move before dispatch (Orchestrator,
step 2). A single-file spec in the packet returns BLOCKED naming that
step.

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
the pins live in `info`, next to `info.x-reviewed` (set by `doc-review`; do not
write it). Pin the SRS and, when
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
security: []   # the SRS named no scheme, so no 401/403 below; otherwise the named scheme (Step 4)
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
                $ref: "#/components/schemas/ResourcePage"
              example:
                items: []
                next_cursor: null
        "500":
          $ref: "#/components/responses/InternalError"
components:
  schemas: {}
  responses:
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
- Include `example` or `examples` on every request and response body.
- Mark required fields with the `required` array.
- Use `nullable: true` on a single `type` for a field that may be absent as JSON null. Do not use `type: [string, "null"]`: that is OpenAPI 3.1, and this spec is 3.0.
- Prefer `format` keywords: `int32`, `int64`, `float`, `date`, `date-time`, `uuid`, `email`, `uri`, `byte`, `binary`.
- **Property casing is the column casing.** A stored property is the column
  name verbatim (`snake_case`, e.g. `starts_at`). Wrapper, computed, and query
  and path parameter names use the same casing (`page_size`, `next_cursor`,
  `user_id`). Do not mix camelCase and snake_case property names in one
  spec; `operationId` stays camelCase.

**Base schemas.** Read `references/base-schemas.md` before writing
`components`: the page, the error body (`Problem`), the timestamps mixin
and the shared responses, each copied as it stands. One copy of each
lives there, so every spec this skill writes has the same error and page
shape the stack skills implement.

Every 4xx and 5xx response uses `application/problem+json` with `Problem`.
A named use-case error sets `code` to the SRS exception name and `type` to
`/problems/<code in kebab-case>`; do not add a second error schema. When an existing spec
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
| `409` | Only as a named use-case error (below) |
| `422` | A body, query, or path field fails its schema (`code: VALIDATION_ERROR` with `errors`), or a named use-case error the SRS sets to 422 |
| `429` | Rate limited |
| `500` | Internal server error |
| `503` | A write lost to a concurrent transaction (serialization failure, deadlock) after the server's own retries; `Retry-After` says when to repeat |

Per operation emit exactly: its success code; one response per named
use-case error; `422` (`VALIDATION_ERROR`) when it takes a body or
parameters; `400` only when it takes a JSON body or a cursor; `401` and
`403` only when the operation is secured; `404` only when the path names a
resource id; `429` only when the SRS names a rate limit; `503` when it
changes stored data in a transaction; `500` always. `409` appears only as
a named use-case error: a uniqueness clash is the use case's named error,
never a bare 409.

**`documentation/api/openapi.yaml` is the one source** for the error body, the validation status,
the casing, and the page shape. Stack skills (`typescript-fastify`,
`fastapi`, test skills) implement what it says and do not
define their own. A code the operation
cannot return misleads `screen-spec` and every generated client.

The status of a **named** use-case error is not chosen from the generic
4xx table: it is the SRS status or the answer in ANSWERS
(Step 1 mapping). Do not stop to wait for an architecture table. A status label
shown to the client is the schema's «Подпись» column in `## Закрытые
наборы значений`, not an example invented here.

Use `$ref` to `components/responses` for `400`, `401`, `403`, `404`,
`422`, `429`, `500`, `503` (`references/base-schemas.md`).

### Step 7 — Quality Checklist

Before delivering the spec, verify:

- [ ] `openapi: "3.0.3"` present, not `3.1.0`
- [ ] `info.version` per Contract version; `info.x-sources` pins each source as `path@<version>` — Step 2
- [ ] Every path has at least one operation
- [ ] Every operation has a unique camelCase `operationId` matching a use case or query — Step 1
- [ ] Every operation has exactly the codes Step 6 derives: a success code, `500`, one response per use-case failure with the Step 1 status
- [ ] Success bodies and field names match the use case and the schema's DBML — Step 1
- [ ] `required` and an `example` on every request and response body — Step 3
- [ ] Security per Step 4; every `callbacks:` entry has a signature header
- [ ] Tags defined at root level to match operation tags
- [ ] `redocly lint` (recommended) reports no `error` (an unresolved `$ref` is one) and no `no-unused-components` warning (an orphaned schema), or the close says why it could not run

### Step 8 — Output

**Layout.** The contract is split into files, so a reader opens the
operation or schema it needs instead of thousands of lines. It is the layout
`redocly split` produces and `redocly bundle` reverses:

```text
documentation/api/
├── openapi.yaml                    root: openapi, info (version, x-changelog,
│                                   x-sources), servers, security, tags; every
│                                   path and component listed by $ref
├── paths/bookings_{id}.yaml        one file per path: /bookings/{id}
└── components/
    ├── schemas/Booking.yaml        one file per schema
    ├── responses/ProblemResponse.yaml
    ├── parameters/…
    └── securitySchemes/…
```

- `openapi.yaml` keeps its path, so `openapi.yaml@<version>` citations,
  the linter and the client generators keep working: they follow the
  `$ref`s. A generator that cannot reads a bundle made in the build
  (`npx --yes @redocly/cli bundle documentation/api/openapi.yaml -o
  <build dir>/openapi.bundled.yaml`), never a committed second copy.
- A new path gets its own file named as `redocly split` names it (`/` →
  `_`, braces kept); a new schema, response or parameter its own file
  under `components/`; both are listed in the root. A path file refers to a
  schema by its file (`$ref: ../components/schemas/Booking.yaml`).
- Searching the contract — an `operationId`, a schema, a status — runs over
  `documentation/api/`, not over the root alone.

1. `doc-typist` writes `documentation/api/openapi.yaml` and every file it
   references (the paths `doc-versioning` names); the orchestrator lints the
   root.
2. The report has exactly the packet's fields. A use case left without an
   operation goes to CONCERNS; no summary table.
3. Do not run `doc-review` or `pipeline` — the orchestrator closes the stage.

Do not rewrite use-case Steps inside the spec. Do not ask to generate
test cases, mock servers, or client SDKs unless the user asks.

## Reference Files

- `references/base-schemas.md` — the page, `Problem`, timestamps and shared responses; before writing `components`
- `references/security-schemes.md` — OpenAPI 3.0 security schemes; when the SRS names auth
- `references/common-patterns.md` — pagination, problem+json, webhooks, file upload, filtering; when the SRS
  names one of them, not by default
- `references/descriptions.md` — when writing any description (`info`, operation, schema, property)
