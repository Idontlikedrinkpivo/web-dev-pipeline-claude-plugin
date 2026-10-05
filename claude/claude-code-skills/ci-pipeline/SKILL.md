---
name: ci-pipeline
description: >-
  Writes `.github/workflows/ci.yml`: a hardened GitHub Actions workflow that
  re-runs the project's own lint, typecheck and tests on every push and PR
  against `docker-compose.test.yml`; adapts the same checks to GitLab CI or
  CircleCI. Use after `deploy-topology` when the user asks for CI, GitHub
  Actions, PR checks, or «чтобы сломанный код не попал в main». Not for CD,
  release images, branch protection, the test topology (`deploy-topology`),
  or adding lint and test tooling the repo lacks.
---

# CI Pipeline

CI is the independent re-check, not a second definition of "passing". Every
step in the workflow this skill writes calls a command the project already
has — `make lint`, `make typecheck`, `make test` (or `npm run lint`,
`npm run typecheck`, `npm test`), the targets `repo-scaffold` created — and
never introduces a parallel rule set that can drift from what a developer
runs on their own machine.

**Why this matters more than usual in this pipeline:** `work` dispatches
subagents to write code, and `code-review-unit`/`code-review-full` are
themselves agents judging that code. Every one of those is a claim about the
tree at one point in time, made by something that can misreport. CI is the
one deterministic, non-agentic re-check: same commands, clean checkout, every
push — the thing that catches "the worker's report said tests passed but the
test file was never committed" class of failures at the repository level
instead of trusting the run report.

## Scope

**USE when:**
- `deploy-topology` has already produced `docker-compose.test.yml` and the
  project has lint/typecheck/test commands (Makefile, `package.json`
  scripts, or the stack's task runner)
- The user asks for CI, a GitHub Actions workflow, automated checks on PRs,
  or "make sure this can't merge broken"

**NOT for:**
- CD — building/pushing a release image, deploying to the prod topology
  `deploy-topology` defined. That is the user's shipping flow, same
  exclusion `work` and `deploy-topology` already state.
- Branch protection rules, required-reviewers settings, merge queues — repo
  settings the user configures once in the platform's UI; this skill can
  name which check names to require, not set the setting.
- Inventing a check the project doesn't already run locally. If there is no
  `lint` command yet, that is a gap in the project's own tooling, not
  something CI papers over by inlining a linter invocation nobody runs
  outside CI. The optional `security` job (Step 7) is the one bounded
  exception, and it says how it comes back under this rule.
- Provisioning real secrets, deploy credentials, or anything beyond the
  test-fixture values `docker-compose.test.yml` already uses in the clear.

## Inputs

| Input | Required | Source |
|---|---|---|
| The project's own check commands | **yes** | `Makefile`/`package.json`/task runner — `lint`, `typecheck`, `test`, and any per-language test command |
| `docker-compose.test.yml` | **yes** | `deploy-topology` — the exact fixture credentials, images, and versions this workflow's service containers must match |
| Stack / language | **yes** | architecture §1 Стек — picks the setup action and cache strategy |
| CI provider | ask if not obvious | GitHub Actions is the default below; for another provider see `references/providers-and-stacks.md` |

Without the project's own commands already existing, stop and name the gap
— do not write `ruff check .` directly into the workflow when there is no
local `lint` target calling it; add the target first, or hand back to
whichever skill owns that tooling. Without `docker-compose.test.yml`,
stop the same way: do not invent infra services or emit a workflow —
hand back to `deploy-topology`, since CI can only mirror a test topology
that already exists.

## Output

Write **`.github/workflows/ci.yml`** (GitHub Actions default). Required
top-level keys: `name`, `on`, `jobs`. Do not leave the workflow as a
snippet in a note. Other providers keep the same shape under their own
path (`.gitlab-ci.yml`, etc.).

Start from `references/ci-skeleton.md` — one complete minimal workflow
with the Step 6 hardening already in place, in a compose variant and a
service-containers variant. Read it before writing the file; the steps
below say why each part is there. The skeleton shows GitHub Actions with
a Python and a Node job. When the provider or a toolchain differs, read
`references/providers-and-stacks.md`: it maps each part of the skeleton
to the key or setting that carries it there, and gives the setup step
and cache per toolchain.

## Workflow

### Step 1. One job per independently-cacheable toolchain

Split by language/toolchain, not by check type — a Python lint failure
should not block a frontend test job from reporting, and each job gets its
own dependency cache keyed on that toolchain's lockfile. Do not merge every
check into one long job "to keep it simple"; the point of separate jobs is
that a frontend-only PR gets its frontend feedback without waiting on the
Python job's install step.

### Step 2. Reuse the test topology's exact fixture shape

Every credential, image tag, and port this workflow's services declare must
match `docker-compose.test.yml` value for value — same Postgres image and
version, same fixture user/password/db name, same S3-compatible store
image (SeaweedFS by default), access keys and bucket name. Two sources of truth for "what does the test
environment look like" drift apart the first time one of them is updated and
the other is not.

Prefer starting the infrastructure straight from the test compose file
when every infra service in it publishes its port on `127.0.0.1`:
`docker compose -f docker-compose.test.yml up -d --wait <db> <store>`,
then `docker compose -f docker-compose.test.yml run --rm <store>-init` —
infra services only, never `app` or `migrate`. The one-shot init stays out
of `up --wait`: `--wait` treats its normal exit as a failure
(docker/compose#10596). The fixture values then
have one source and cannot drift; the language toolchain still runs on
the runner and reaches the services on `127.0.0.1`, as `make test` expects.

Fall back to `references/service-containers.md` only when a needed port
is not published or the runner has no Docker Compose. It shows each infra
dependency the provider's native way. On GitHub Actions that is a native
service container for every dependency — services accept `command:` and
`entrypoint:` since April 2026 — plus one step for the bucket init. A
manually-run container plus a readiness-poll loop is only for a provider
whose service config cannot override the image's command. When you fall
back, the fixture values are a copy — the
`Drifted fixtures` guardrail applies.

Host-side env on the runner is a second copy of the fixture contract, not
a new one. Must match `docker-compose.test.yml` and still be reachable
from the language job:

| Must copy onto the runner | Why |
|---|---|
| Image / user / password / db name | Same fixture the compose file already publishes |
| `APP_ENV=test` | Fail-fast config; mock gate only legal in test |
| Mock-gate variable | `${{ github.workspace }}/<mock-fixtures-dir>` — the runner's checkout of the fixtures, so tests make zero outbound calls |
| `DATABASE_URL` (and object-store URL) | **Host** `127.0.0.1`, not the compose service hostname; same `search_path` / schema as compose |

A URL that still says `@postgres:5432` will fail on the runner. Do not
re-decide the schema name here.

### Step 3. Migration before test, same command as `migrate`

Run the schema migration as its own step, using the exact command
`docker-compose.test.yml`'s `migrate` service runs — not a reimplementation.
Skip it and tests fail against an unmigrated schema; reinvent it and a
second invocation quietly drifts from the one the test compose documents
as canonical. If the project's test suite already migrates itself (a fixture in
`conftest.py`/equivalent that runs migrations once per session), this step
is unnecessary; check before adding a redundant one.

### Step 4. The check steps are one line each, calling the existing command

```yaml
- name: Lint
  run: make lint
- name: Typecheck
  run: make typecheck
- name: Test
  run: make test
```

Not `ruff check .`, not `mypy app` inlined — `make lint` / `make typecheck`.
The workflow file's job is plumbing (checkout, toolchain setup, service
containers, caching), never a second copy of what the command does. This is
what keeps "green in CI" and "green locally" the same claim.

`make test` (or its equivalent) already includes the compose-contract tests
and the `.env.example`-sync test from `deploy-topology`, because those live
in the project's own test suite — do not add a separate CI step for them and
do not scope the test runner's invocation to exclude the file they live in.

**Browser e2e** (a frontend with a `test:e2e` target — `repo-scaffold`,
`frontend`): add it as its own job, `e2e`, that installs the browsers the
Playwright config names, starts the app the way the config's `webServer`
does, and runs `npm run test:e2e` — the same command a developer runs. When
the repo has no such target, the workflow has no e2e step, and the close
(Step 8) says that browser tests are not in CI.

### Step 5. Triggers

`push` on the default/integration branch, and `pull_request` on every
branch — a check that only runs after merge catches the break too late to
be a gate. Do not add a schedule/cron trigger here; that belongs to whatever
periodic job the project needs (dependency audit, etc.), a different concern
from "does this change break the build" with different failure handling
(nobody is blocked on a nightly job) — a separate workflow file if the
project needs one. The PR-time `security` job of Step 7 is not that job:
it answers "did this change add a vulnerable dependency or a secret" on
the same triggers as the rest.

### Step 6. Harden the workflow skeleton

This workflow runs on every pull request, so its token and its actions
are an attack surface even though it holds no secrets. The items below
are GitHub Actions syntax; on another provider keep each item's intent
through the key or setting `references/providers-and-stacks.md` names.

- Top-level `permissions: contents: read`. Widen per job only when a step
  needs it, and name that step.
- Pin every action to a full-length commit SHA with the tag in a trailing
  comment (`uses: actions/checkout@<sha> # v7`). A tag can be moved; a SHA
  cannot. Do not copy a major from memory or from this file: resolve the
  latest major tag with `git ls-remote --tags` and pin its SHA
  (`references/ci-skeleton.md`).
- `actions/checkout` with `persist-credentials: false` — no later step
  pushes.
- `timeout-minutes` on every job, sized to a few times the normal run,
  so a hung service container does not burn the default six hours.
- `concurrency: { group: ${{ github.workflow }}-${{ github.ref }},
  cancel-in-progress: true }` so a new push to the same PR cancels the
  stale run.
- Dependency cache through the setup action's own cache input
  (`setup-python` `cache: pip`, `setup-node` `cache: npm`; other
  toolchains in the reference) before reaching for `actions/cache`, so
  the key follows the lockfile without a hand-written key.
- Never `pull_request_target` for this workflow: it runs fork code with
  the base repository's token and secrets.

### Step 7. Optional `security` job: included, advisory until opted in

Default: include it; omit it only when the user declines or an equivalent
scanner already runs on the same pull requests. It needs no secrets, and a
change that adds a known-vulnerable dependency or a committed key is
exactly what an agent-written diff can carry past an agent review. It
stays **advisory** until the team opts in: new advisories land against an
unchanged lockfile, so a gate that turns red on untouched code from day
one teaches everyone to ignore red. YAML: `references/ci-skeleton.md`
(GitHub Actions), `references/providers-and-stacks.md` (GitLab CI, audit
command per toolchain).

- **Shape.** One `security` job beside the toolchain jobs, so its result
  never hides theirs: a secret scan, then one audit step per toolchain the
  project has. No dependency install, no infra, no cache. Every step after
  the first runs `if: ${{ !cancelled() }}` so one run reports all of them.
- **Threshold.** Dependency audit fails on high and critical and prints the
  rest. A tool with no severity filter fails on any known advisory;
  accepted exceptions go through its ignore-by-ID option, each with the
  advisory ID and a one-line reason next to the command. The secret scan
  fails on any finding; false positives — including the fixture values in
  `docker-compose.test.yml`, test values in the clear by design — go in
  the scanner's committed allowlist by path, never a blanket disable.
- **Scope of the secret scan.** Full history of the checkout, not the final
  tree: a key added in one commit of a PR and deleted in the next is still
  leaked. Redact findings in the log — the log is public on a public repo.
- **Command source.** If the project has an audit target (`make audit`,
  `npm run audit`), call it — Step 4. If not, this job may call the tool
  directly, because an advisory check defines no "passing"; before it
  becomes required, that command moves into a local target and the step
  calls the target.
- **Version-sensitive flags.** Severity flags and scanner subcommands
  change between releases. Check each against the pinned version's
  `--help` or current docs (context7) before writing it; the flags in the
  references are examples, not facts. The scanner image is pinned by
  digest, a tool installed by pip/npm at an exact version, like any action
  in Step 6. Do not use a wrapper action that asks for a license key or
  any other secret.
- **Posture unchanged.** Top-level `permissions: contents: read`; no
  `security-events: write` or SARIF upload unless the user asks, and then
  on this job only; no `pull_request_target`; no schedule here (Step 5).
- **Advisory, and how it becomes required.** GitHub Actions / CircleCI:
  the job fails honestly on its threshold and is simply not in the
  required checks — no `continue-on-error`, which turns a finding into a
  green check nobody opens. Making it required = adding `security` to
  branch protection. GitLab CI: `allow_failure: true` on its jobs, since
  "pipelines must succeed" would otherwise block the MR; removing it is
  the opt-in.

### Step 8. Say what the user still has to do by hand

An unenforced CI only reports, and a PR can merge past a red run, so the
user has to hear what is still missing. Close by telling the user, in
this order:

1. The check job names this workflow produces, and whether browser e2e is
   one of them (Step 4).
2. To mark them required in the repo's branch-protection settings.
3. That this skill did not enable branch protection and cannot — it is a
   repository setting outside the workflow file.
4. That until they do, a red run blocks no merge.
5. Any other provider setting the workflow depends on (token scope,
   auto-cancel, fork-secret policy — `references/providers-and-stacks.md`).
6. If the `security` job is in: that it is advisory and not in the list
   from item 1, how to make it required (Step 7), and — when it calls a
   tool directly — that the command moves into a local target first.

Example close:

> CI добавлен: `.github/workflows/ci.yml`, проверки `backend` и
> `frontend`. Отметьте обе как required в Settings → Branches → branch
> protection для `main`. Сам навык branch protection не включал и включить
> не может; пока вы этого не сделаете, красный прогон не блокирует merge.
> Job `security` (аудит зависимостей и поиск секретов) пока
> рекомендательный: падает на high/critical, но в required не входит.
> Чтобы сделать его обязательным, сначала вынесите команду аудита в
> `make audit`, затем добавьте `security` в required.

## Guardrails

- **Drifted fixtures.** On the fallback path, a Postgres version or an
  object-store bucket name in the workflow that no longer matches `docker-compose.test.yml` because one was
  updated and the other forgotten. Grep both files for the values this
  workflow hardcodes when touching either.
- **Real secrets in the workflow.** Only test's fixture values, the same
  ones already visible in `docker-compose.test.yml`, belong here. Anything
  that would matter if leaked has no business in a CI job that runs on every
  fork's pull request.

## Before you finish

- `.github/workflows/ci.yml` (or the provider's path) with `name`, `on`,
  `jobs` — Output.
- One job per toolchain — Step 1.
- Fixture values match `docker-compose.test.yml` exactly — Step 2.
- Migration once, before tests, or confirmed redundant — Step 3.
- Every check step calls an existing local command — Step 4.
- `push` + `pull_request`, no schedule — Step 5.
- Every Step 6 hardening item is present; no `<sha>` or `<digest>` placeholder is left.
- `security` job present (or declined), advisory, thresholds and flags checked against the pinned tool versions, no secrets — Step 7.
- The user was told the check names, to mark them required, that the skill did not enable branch protection, and that CI blocks nothing until they do — Step 8.

## References

- `references/ci-skeleton.md` — the complete minimal `ci.yml` to start
  from (compose variant and service-containers variant), plus the
  optional `security` job.
- `references/service-containers.md` — the native-service-container pattern
  per infra dependency, and the manual-container fallback for images the
  provider's service config cannot start correctly.
- `references/providers-and-stacks.md` — what carries each skeleton part on
  GitLab CI / CircleCI, and the setup step and cache per toolchain. Read
  when the provider is not GitHub Actions or a toolchain is not Python / Node.
- `deploy-topology` (skill) — the test topology and fixture values this
  workflow must mirror exactly.
- `pipeline` (skill) — this is the last stage in it. Nothing follows: say the
  workflow is in place and stop, rather than inventing a next step. Shipping is
  the user's own flow.
