# Other providers and other toolchains

Read when the CI provider is not GitHub Actions, or a job's toolchain is not
the Python / Node pair the skeleton shows. The shape does not change: one
job per toolchain, fixture values copied from `docker-compose.test.yml`,
migrate before test, every check step calls the project's own command, and
the hardening intent of Step 6. Only the syntax and the setting that
carries each part move.

## Provider: what carries each part

| Part (Step) | GitHub Actions | GitLab CI | CircleCI |
|---|---|---|---|
| File | `.github/workflows/ci.yml` | `.gitlab-ci.yml` | `.circleci/config.yml` |
| Triggers (5) | `on: push` (default branch) + `pull_request` | `workflow: rules:` — merge-request pipelines plus the default branch | every pushed branch by default; PR-only builds are a project setting |
| Job per toolchain (1) | one `jobs.<id>` each | one job each, its own `image:` | one job each, listed in a `workflows:` entry |
| Least-privilege token (6) | `permissions: contents: read` | job-token scope — a project setting; name it to the user | no file key; keep secrets out of contexts this workflow uses |
| Pinning (6) | action at a full commit SHA | `image:` by digest; `include:` with `ref:` at a commit SHA | orbs at an exact `x.y.z`, never `volatile` or a dev orb |
| Timeout (6) | `timeout-minutes` per job | `timeout:` per job | `no_output_timeout` per step |
| Cancel stale runs (6) | `concurrency` + `cancel-in-progress` | `interruptible: true` + "auto-cancel redundant pipelines" | "auto-cancel redundant workflows" setting |
| Cache (6) | setup action's `cache:` input | `cache: key: files: [<lockfile>]` | `restore_cache` / `save_cache` keyed on `{{ checksum "<lockfile>" }}` |
| Infra from compose (2) | `docker compose ... up -d --wait` on the runner | needs a Docker-in-Docker service; prefer native `services:` | `machine` executor has Docker Compose |
| Native service containers (2) | `services:`, reached on `127.0.0.1` | `services:` with `alias`, reached **by the alias hostname** | secondary images under `docker:`, reached on `localhost` |
| Fork code with base secrets (6) | never `pull_request_target` | do not run fork MR pipelines in the parent project | keep "pass secrets to forked PRs" off |
| Advisory `security` job (7) | not in required checks; no `continue-on-error` | `allow_failure: true` per job; `GIT_DEPTH: "0"` on the secret scan | not in required checks |

A row that is a project setting rather than a file key goes into the Step 8
message beside branch protection: the skill cannot set it, so the user has
to.

On GitLab, native `services:` are reached by alias, so `DATABASE_URL`'s
host is that alias, not `127.0.0.1`. The fixture user, password, db name,
and `search_path` still copy from `docker-compose.test.yml` unchanged.

## Toolchain: the setup step and its cache

Only the setup step and the cache key change per toolchain. The check steps
still call the project's own commands (`make`, `npm run`, `task`, `just`,
`./gradlew check`) — whatever the developer runs locally.

| Toolchain | GitHub setup step | Cache | Version from |
|---|---|---|---|
| Python (pip / Poetry) | `actions/setup-python` | `cache: pip` or `poetry` | `python-version-file` |
| Python (uv) | `astral-sh/setup-uv` | `enable-cache: true` | `.python-version` |
| Node (npm / yarn) | `actions/setup-node` | `cache: npm` or `yarn` | `node-version-file` |
| Node (pnpm) | `pnpm/action-setup`, then `actions/setup-node` | `cache: pnpm` | `node-version-file` |
| Go | `actions/setup-go` | on by default, keyed on `go.sum` | `go-version-file: go.mod` |
| Java / Kotlin | `actions/setup-java` (`distribution` required) | `cache: maven` or `gradle` | `java-version` |
| .NET | `actions/setup-dotnet` | `cache: true` (needs `packages.lock.json`) | `global-json-file` |
| Ruby | `ruby/setup-ruby` | `bundler-cache: true` | `.ruby-version` |
| Rust | `dtolnay/rust-toolchain` | `Swatinem/rust-cache` step | `rust-toolchain.toml` (rustup reads it) |

Pin each of these to a commit SHA like any other action (Step 6). The
migrate step stays whatever command the `migrate` service in
`docker-compose.test.yml` runs, whatever the language.

## The `security` job (SKILL Step 7)

### Audit command per toolchain

The threshold is the same everywhere: fail on high and critical, print the
rest. Prefer the project's own `audit` target when it exists (Step 4).
Every flag below is version-sensitive — confirm it in the pinned
version's `--help` or current docs (context7) before writing it.

| Toolchain | Audit command (example) | Threshold note |
|---|---|---|
| Node (npm) | `npm audit --audit-level=high` | reads `package-lock.json`; no install needed |
| Node (pnpm) | `pnpm audit --audit-level high` | needs pnpm set up, not an install |
| Node (yarn) | classic and Berry differ (`yarn audit` vs `yarn npm audit`), and so does the severity flag | check which yarn the repo pins |
| Python (pip / Poetry / uv) | `pip-audit -r <requirements exported from the lockfile by the project's own tool>` | check `pip-audit --help` for a severity filter; without one it fails on any known advisory, and accepted ones go through `--ignore-vuln <ID>`, each with a reason |
| Other toolchains | the ecosystem's own advisory tool | same rule: severity flag if it has one, otherwise any advisory fails and exceptions go by ID |

### GitLab CI shape

A GitLab job has one image, so the secret scan and each audit are separate
jobs, all `allow_failure: true` until the team opts in (removing it is the
opt-in). They inherit `workflow: rules:`, so they run on the same MR and
default-branch pipelines as the checks. Images by digest, as in the table
above; no CI/CD variables, no secrets.

```yaml
secret-scan:
  image:
    name: <gitleaks-image>@sha256:<digest>
    entrypoint: [""]
  variables:
    GIT_DEPTH: "0"                     # full history
  allow_failure: true                  # advisory (SKILL Step 7)
  interruptible: true
  timeout: 10m
  script:
    - gitleaks git --redact --verbose .   # subcommand/flags: verify against the pinned version

audit-<toolchain>:                     # one per toolchain the project has
  image: <toolchain image>@sha256:<digest>
  allow_failure: true
  interruptible: true
  timeout: 10m
  script:
    - <make audit, or the command from the table above>
```

GitLab also ships its own secret-detection and dependency-scanning
templates; what they include depends on the instance version and tier —
verify in current docs before choosing one over the jobs above, and keep
them `allow_failure` until the team opts in.
