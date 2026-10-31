---
name: security-audit
description: >-
  Audits the whole app's security before release: scanners, then each API operation traced route to data. Use for
  «проверь безопасность», «аудит безопасности», «нет ли уязвимостей». A PR or diff: /security-review.
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
| Code quality, dead code, debt | `code-review-full` per run; across the whole code: `upgrade-code` → Code audit |

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
then post its progress line, and again after each row: run
`python3 "${CLAUDE_SKILL_DIR}/../pipeline/scripts/progress_link.py" documentation/plans/<version>/security-audit.md`
(`--desktop` when this session has the built-in browser) and paste the line it
prints, never a link written by hand; after each area returns, check the context (`pipeline` →
`references/context.md` → When to hand over). Change the file with Edit only — never
from the shell, also after a compaction: the page redraws on Edit and Write
alone. Keeping the run moving applies: every
turn ends with the next scanner or auditor running. Its shape:
`references/report.md`.

The audit is a long run, so it keeps the resume note too (`pipeline` →
`references/pause-and-resume.md`): read
`documentation/plans/<version>/resume.md` first when one is there, refresh it
after each row — a scanner, an area, the verify pass — with the auditors still
out and the findings not yet verified, and delete it when the verdict line is
written. A note left behind sends the next session after an audit that is
over.

## Steps

### 1. Scanners

The scanners read the files and the history: they need no running
application. When the project has a verify skill (`.claude/skills/verify/`),
read its Traps first — a proxy or a cache already met there applies to the
scanners too — and add any network trap the scanners meet. Without one, do
not write it here: on a first iteration the test stand does not exist yet
(`deploy-topology`, the stage after this one, builds it). Run each scanner from
`references/scanners.md` over the repository root,
through its Docker image (nothing installed on the machine); without
Docker, the local tool, then say which way it ran. Save each raw output
under `$(git rev-parse --git-dir)/pipeline-work/security/`, never paste it.

| Scanner | Finds |
|---|---|
| dependencies — `osv-scanner` (or `npm audit` / `pip-audit`) | known vulnerabilities in the locked versions |
| secrets — `gitleaks` | keys, tokens, passwords in files **and in history** |
| patterns — `semgrep`, OWASP and stack rule packs | injection, unsafe deserialization, disabled TLS checks, weak crypto, `eval` |

A scanner that cannot run is a row `⏭ пропущено: не запускался — <причина>` and a line
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
limits, logging, password storage and the account rules, the frontend
(raw HTML from user text, secrets in the bundle, where the session token
lives) — and the scanner findings to triage.

Each auditor follows every operation from the route to the data and back,
and returns findings with `file:line`, the concrete request that exploits
it, the rule it breaks, and a fix in words. Every auditor numbers its own
findings from F1, so when the reports are in, renumber them into one
sequence — F1, F2… in area order, the app-wide ones last — and use only that
number from then on: in the verify packet, the report and the questions to
the user.

### 4. Verify

Confirm each P0 and P1 quotes a line that exists. **The proof is what the
finding is made of, not a running stand.** A scanner finding is proven by
its output and the code line it points at. A trace finding carries its
exploit request: when the test stand is already up (the verify skill's
doctor says READY), send that request to it yourself — `curl` for an API
operation, the browser only for a step that exists only on a screen — and
write the answer under the finding. With no stand up, or none yet, the
finding stands on the traced code and the verify pass, and the report says
so: «запросом не проверено: стенда нет». The audit never builds or starts a
stand. Then dispatch
`security-auditor` once in `MODE verify` with only those findings: it tries
to **disprove** each — a middleware that already checks, a query already
scoped to the owner, a path unreachable from outside — and keeps what it
cannot disprove. A disproved finding goes to «Отклонено» with the reason.
P2 and P3 are not verified: they block nothing.

**Against a settled decision.** Before the verdict, check every finding —
P0 to P3 — against the SRS (NFR, BR), architecture §1 «Решения по
безопасности» and «Принятые риски», and the project's decisions log. A finding
that a document already decided on purpose («предела по адресу нет») is
marked `⚖ против решения <id>` and is never fixed, planned or sent to the
report as a fix: it goes to the user as a question with that decision
quoted (`pipeline` → `references/decision-changes.md` → A finding against a
settled decision).

### 5. Verdict and next step

- `PASS` — no P0 or P1 open. Offer `deploy-topology` (`pipeline` → Asking
  before a transition).
- `FIX` — P0 or P1 open. Show them one per message, per `grill-me` → "How
  a question is shown" — a `⚖ против решения` finding first, with its
  decision quoted — each with the options «A. Исправить»,
  «B. Принять риск» — the user's reason goes into the report, and an
  accepted finding no longer blocks; the risk also goes into architecture
  §1 «Принятые риски» with that reason and the date, through `pipeline` →
  `references/decision-changes.md`, because this report is removed when
  the iteration closes and the next audit reads accepted risks there — and
  «C. Отложить» (stays open). Then
  offer a fix plan: `plan` over the findings marked A, one unit per fix or
  per shared cause, then `work`. After that run, re-audit only what it
  touched: the fixed findings plus the scanners (`pipeline` →
  `references/convergence.md`). The recommendation comes from the evidence:
  «Принять риск» when the finding goes against a settled decision and shows
  no way to break the application that the decision missed.

An open P0 blocks the release: `deploy-topology` does not build the image
archive while this report holds one, unless the user says to build anyway
(that answer is recorded in the report).

## Severity

P0 to P3 with examples: `references/auditor-prompt.md` → Severity — one copy, so the
auditors and this session grade on the same scale.

A finding the documents cause — two readings of who may do what, a missing
rule — is owned by the document: it goes to the SRS or the architecture
through `pipeline` → `references/decision-changes.md` once the user
decides.

## Before you finish

- Every scanner ran or has its `⏭ пропущено: не запускался` row — Step 1.
- Every operation of the contract is a matrix row, and every row was traced
  by an auditor — Steps 2–3.
- Every P0 and P1 survived the verify pass or sits in «Отклонено» with a
  reason, and says whether a request to the stand confirmed it — Step 4.
- The finding numbers are one sequence across the auditors — Step 3.
- `resume.md` is gone once the verdict line is written — Progress and report.
- The report's first line is the verdict; every open P0/P1 has the user's
  choice — Step 5.
- Every accepted risk is written into architecture §1 «Принятые риски» with
  its reason and date — Step 5.

## References

- `references/scanners.md` — the scanner commands, Docker images, output
  locations, and how to read each output.
- `references/auditor-prompt.md` — the `security-auditor` packet, its
  lenses, and the report it returns; `MODE verify`.
- `references/report.md` — the shape of `security-audit.md`.
- `executor-catalog` (skill) — `security-auditor`.
- `pipeline` (skill) — stage 14; read it when the audit closes.
