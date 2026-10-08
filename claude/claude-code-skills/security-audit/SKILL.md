---
name: security-audit
description: >-
  Audits the whole application's security once per iteration, before the
  release is built: scanners over all the code and git history (vulnerable
  dependencies, secrets, OWASP patterns), then an Opus auditor per area
  tracing every OpenAPI operation from route to data — authentication,
  access per role from the SRS, other users' data (IDOR), input at the
  boundary, data and errors leaking out, the SRS security requirements and
  the architecture's security decisions — and a second pass that tries to
  disprove each blocking finding. Writes `security-audit.md` with one
  verdict; P0/P1 become a fix plan. Use after `work` and the UI acceptance
  run, before `deploy-topology`, or when the user asks «проверь
  безопасность», «аудит безопасности», «нет ли дыр», a security or OWASP
  review of the app. Not the per-run code reviews, a penetration test of a
  live server, or fixing the code.
---

# Security Audit

The per-run reviews read what one plan changed. Nothing there asks whether
the application **as a whole** can be broken: an operation written three
iterations ago that never checks the owner, a secret committed and removed
since, a dependency that got a CVE last week. This stage asks that, once per
iteration, before the release leaves the machine.

It is an audit of the **attack surface**, not a line-by-line read. Scanners
cover every file and the whole history cheaply; the model's work goes where
web applications are actually broken — routes, access checks, other users'
data, input and output at the boundary, secrets and configuration. Reading
every file looking for "something suspicious" costs much and finds noise.

Write the report and every user-facing message in Russian. Do not translate
ids (`FR-`, `NFR-`, `BR-`, `UC-`, `operationId`, `UX-`), file paths or tool
names.

## Not this skill's job

| Not here | Owner |
|---|---|
| Reviewing one plan's diff | `code-review-unit`, `code-review-full` |
| Fixing what the audit finds | a fix plan: `plan` → `work` |
| Deciding which security requirements exist | the SRS security checklist, the architecture's security decisions, `doc-review`'s security lens |
| Scanning the built Docker images | `deploy-topology` Step 8, where the images exist |
| Attacking a running server, load, fuzzing, infrastructure | outside this pipeline |
| Code quality, dead code, debt | `code-review-full` per run |

## Inputs

| Input | Required | Use |
|---|---|---|
| The code at `HEAD`, and git history | **yes** | scanners, then the trace |
| OpenAPI (`documentation/api/`) | **yes** when there is HTTP | the operations to trace, security schemes, response fields |
| SRS (`srs.md` and areas) | **yes** | actors and roles, who may do what (UC actors, BR rows), the security NFR rows |
| Architecture foundation | **yes** | the security decisions table, areas, configuration variables, where auth is wired |
| Project map | when present | where each area's code lives |
| DB schema | when present | owner columns, sensitive columns |
| The previous `security-audit.md` of this iteration | on a re-audit | which findings were fixed or accepted |

No OpenAPI (a worker, a CLI): trace the entry points the architecture names
instead — queue consumers, scheduled jobs, CLI commands — with the same
lenses.

## Progress and report

The report is `documentation/plans/<version>/security-audit.md`, out of git
like the stage's other files, and it is the progress file too (`pipeline` →
`references/progress-files.md`): create it before the first scanner with
every row `⏳ ждёт` — one per scanner, one per area, the verification pass —
post its link, and write the count with the link after each row (Keeping
the run moving applies: every turn ends with the next scanner or auditor
running). Its shape: `references/report.md`.

## Steps

### 1. Scanners

Run each scanner from `references/scanners.md` over the repository root,
through its Docker image (nothing installed on the machine); without
Docker, the local tool, then say which way it ran. Save each raw output
under `$(git rev-parse --git-dir)/pipeline-work/security/`, never paste it.

| Scanner | Finds |
|---|---|
| dependencies — `osv-scanner` (or `npm audit` / `pip-audit`) | known vulnerabilities in the locked versions |
| secrets — `gitleaks` | keys, tokens, passwords in files **and in history** |
| patterns — `semgrep`, OWASP and stack rule packs | injection, unsafe deserialization, disabled TLS checks, weak crypto, `eval` |

A scanner that cannot run is a row `⚠️ не запускался: <причина>` and a line
in the verdict, never a silent skip. Check each tool's flags against the
pulled version (`--help`) before relying on them.

### 2. The access matrix

Build it from the documents before reading code: one row per operation —
`operationId`, method and path, the security scheme, who may call it (the
SRS actors and rules: «только автор брони», «только администратор»), and
whose data it touches (an owner column, a path id). This is the yardstick
the trace measures against; an operation the documents leave unclear is a
finding itself (`documents`), not a guess.

### 3. Trace by area

Read `executor-catalog` and resolve `security-auditor`. Dispatch one per
area (the architecture's areas, or OpenAPI tags), in parallel, in the
background, with the packet in `references/auditor-prompt.md`: the area's
matrix rows, the code paths from the project map, the SRS security rows
and rules on rights, the architecture's security decisions. One more
dispatch takes the application-wide lenses — authentication wiring,
sessions and cookies, CORS, CSRF, headers, configuration defaults, rate
limits, logging — and the scanner findings to triage.

Each auditor follows every operation from the route to the data and back,
and returns findings with `file:line`, the concrete request that exploits
it, the rule it breaks, and a fix in words.

### 4. Verify

Confirm each P0 and P1 quotes a line that exists. Then dispatch
`security-auditor` once in `MODE verify` with only those findings: it tries
to **disprove** each — a middleware that already checks, a query already
scoped to the owner, a path unreachable from outside — and keeps what it
cannot disprove. A disproved finding goes to «Отклонено» with the reason.
P2 and P3 are not verified: they block nothing.

### 5. Verdict and next step

- `PASS` — no P0 or P1 open. Offer `deploy-topology` (`pipeline` → Asking
  before a transition).
- `FIX` — P0 or P1 open. Show them one per message, per `grill-me` → "How
  a question is shown", each with the options «A. Исправить» (Recommended),
  «B. Принять риск» — the user's reason goes into the report, and an
  accepted finding no longer blocks — and «C. Отложить» (stays open). Then
  offer a fix plan: `plan` over the findings marked A, one unit per fix or
  per shared cause, then `work`. After that run, re-audit only what it
  touched: the fixed findings plus the scanners (`pipeline` →
  `references/convergence.md`).

An open P0 blocks the release: `deploy-topology` does not build the image
archive while this report holds one, unless the user says to build anyway
(that answer is recorded in the report).

## Severity

| | Meaning | Example |
|---|---|---|
| **P0** | exploitable from outside with no special access, data or accounts at stake | an operation returns any user's bookings by id; a live secret in the repo or its history; SQL injection |
| **P1** | exploitable by a signed-in user beyond their role, or a declared security requirement not met | a resident can cancel another resident's booking; no rate limit where an NFR demands one; a known CVE reachable from the app's code |
| **P2** | weakens defence, not exploitable alone | verbose errors with stack traces; a missing security header; a CVE in a dev-only dependency |
| **P3** | hygiene | an outdated but unaffected dependency; a TODO about auth in a comment |

A finding the documents cause — two readings of who may do what, a missing
rule — is owned by the document: it goes to the SRS or the architecture
through `pipeline` → `references/decision-changes.md` once the user
decides.

## Before you finish

- Every scanner ran or has its `⚠️ не запускался` row — Step 1.
- Every operation of the contract is a matrix row, and every row was traced
  by an auditor — Steps 2–3.
- Every P0 and P1 survived the verify pass or sits in «Отклонено» with a
  reason — Step 4.
- The report's first line is the verdict; every open P0/P1 has the user's
  choice — Step 5.

## References

- `references/scanners.md` — the scanner commands, Docker images, output
  locations, and how to read each output.
- `references/auditor-prompt.md` — the `security-auditor` packet, its
  lenses, and the report it returns; `MODE verify`.
- `references/report.md` — the shape of `security-audit.md`.
- `executor-catalog` (skill) — `security-auditor`.
- `pipeline` (skill) — stage 14; read it when the audit closes.
