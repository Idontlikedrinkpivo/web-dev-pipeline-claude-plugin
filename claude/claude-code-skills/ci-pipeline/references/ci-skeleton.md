# CI skeleton: one complete minimal `ci.yml`

Two variants of the same file. Pick by Step 2: **A** when every infra
service in `docker-compose.test.yml` publishes its port on `127.0.0.1` and
the runner has Docker Compose; **B** otherwise. Everything outside the job's
infra part is identical between them.

Placeholders in `<angle brackets>`. Fill every one from the project —
fixture values from `docker-compose.test.yml`, commands from the
`Makefile`/`package.json`/task runner. Never leave one in the written file.
For another toolchain, swap only the setup step and its cache input; for
another provider, translate each part — both in
`references/providers-and-stacks.md`.

`<sha>` is the full-length commit SHA of the tag named in the trailing
comment. The `# v7` below is only an example — do not copy a major from
here. Resolve the latest major tag and its SHA rather than guess, e.g.
`git ls-remote --tags https://github.com/actions/checkout | tail` (same for
`setup-node`, `setup-python`), pick the highest `vN`, and pin its SHA — for
an annotated tag take the commit from the `^{}` line.

## Variant A: infra straight from `docker-compose.test.yml`

```yaml
name: CI

on:
  push:
    branches: [<default-branch>]
  pull_request:

permissions:
  contents: read

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

jobs:
  <backend-toolchain>:                 # e.g. backend
    runs-on: ubuntu-latest
    timeout-minutes: <a few times the normal run, e.g. 20>
    env:
      APP_ENV: test
      DATABASE_URL: <compose fixture URL, host 127.0.0.1, same search_path>
      <OBJECT_STORE_URL_VAR>: http://127.0.0.1:<store-port>
      <MOCK_GATE_VAR>: ${{ github.workspace }}/<mock-fixtures-dir>   # fixtures from the checkout: zero outbound calls
    steps:
      - uses: actions/checkout@<sha> # v7
        with:
          persist-credentials: false
      - uses: actions/setup-python@<sha> # v7
        with:
          python-version-file: <.python-version or pyproject.toml>
          cache: pip
      - name: Install
        run: <the project's own install command>
      - name: Lint
        run: make lint
      - name: Typecheck
        run: make typecheck
      - name: Start test infrastructure
        run: |
          docker compose -f docker-compose.test.yml up -d --wait <db> <store>
          docker compose -f docker-compose.test.yml run --rm <store>-init
      - name: Migrate
        run: <the exact command the migrate service in docker-compose.test.yml runs>
      - name: Test
        run: make test

  <frontend-toolchain>:                # delete if the project has one toolchain
    runs-on: ubuntu-latest
    timeout-minutes: <a few times the normal run, e.g. 10>
    steps:
      - uses: actions/checkout@<sha> # v7
        with:
          persist-credentials: false
      - uses: actions/setup-node@<sha> # v7
        with:
          node-version-file: <.nvmrc or package.json>
          cache: npm
      - name: Install
        run: npm ci
      - name: Lint
        run: npm run lint
      - name: Typecheck
        run: npm run typecheck
      - name: Test
        run: npm test
```

The compose command lists infra services only — never `backend` or `migrate`.
The one-shot `<store>-init` runs with `run --rm`, not inside `up --wait`,
which reports its normal exit as a failure (docker/compose#10596):
the toolchain runs on the runner, which is why every URL in `env:` uses
`127.0.0.1` instead of the compose service hostname. Lint and typecheck
come before the infra start so a style failure reports without waiting on
containers. Drop the `Migrate` step when the test suite migrates itself
(Step 3).

## Variant B: GitHub Actions service containers

Same file as A, except the backend job's infra: Postgres and the object
store (SeaweedFS by default; any S3-compatible image that pulls) as native
service containers, then one step for the bucket. Services accept
`command:` / `entrypoint:`, so the store needs no manual `docker run`;
that fallback, for other providers, is in
`references/service-containers.md`.

```yaml
name: CI

on:
  push:
    branches: [<default-branch>]
  pull_request:

permissions:
  contents: read

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

jobs:
  <backend-toolchain>:
    runs-on: ubuntu-latest
    timeout-minutes: <a few times the normal run, e.g. 20>
    services:
      postgres:
        image: <same image:tag as docker-compose.test.yml>
        env:
          POSTGRES_USER: <same fixture user>
          POSTGRES_PASSWORD: <same fixture password>
          POSTGRES_DB: <same fixture db name>
        ports:
          - 5432:5432
        options: >-
          --health-cmd "pg_isready -U <user> -d <db>"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
          --health-start-period 10s
      <store>:                         # SeaweedFS shape; copy compose's probe for another store
        image: <same image:tag as docker-compose.test.yml>
        # command: <only if docker-compose.test.yml overrides it>
        env:
          AWS_ACCESS_KEY_ID: <same fixture value as compose>
          AWS_SECRET_ACCESS_KEY: <same fixture value as compose>
        ports:
          - <store-port>:<store-port>
        options: >-
          --health-cmd "curl -fsS http://127.0.0.1:<store-port>/healthz"
          --health-interval 5s
          --health-timeout 3s
          --health-retries 10
    env:
      APP_ENV: test
      DATABASE_URL: <compose fixture URL, host 127.0.0.1, same search_path>
      <OBJECT_STORE_URL_VAR>: http://127.0.0.1:<store-port>
      <MOCK_GATE_VAR>: ${{ github.workspace }}/<mock-fixtures-dir>
    steps:
      - uses: actions/checkout@<sha> # v7
        with:
          persist-credentials: false
      - uses: actions/setup-python@<sha> # v7
        with:
          python-version-file: <.python-version or pyproject.toml>
          cache: pip
      - name: Install
        run: <the project's own install command>
      - name: Lint
        run: make lint
      - name: Typecheck
        run: make typecheck
      - name: Create <store> bucket
        run: |
          docker run --rm --network host \
            -e AWS_ACCESS_KEY_ID=<same fixture value as compose> \
            -e AWS_SECRET_ACCESS_KEY=<same fixture value as compose> \
            -e AWS_DEFAULT_REGION=us-east-1 \
            --entrypoint /bin/sh amazon/aws-cli:<pinned-tag> -c \
            '<same command as the <store>-init service in compose, endpoint http://127.0.0.1:<store-port>>'
      - name: Migrate
        run: <the exact command the migrate service in docker-compose.test.yml runs>
      - name: Test
        run: make test

  # <frontend-toolchain>: copy the job from Variant A unchanged, or omit it
```

Every value under `services:` and in the `docker run` line is a copy of
`docker-compose.test.yml` — this is the path where the "Drifted fixtures"
guardrail applies.

## Optional: the `security` job (both variants)

SKILL Step 7. Append under `jobs:` of either variant; nothing else in the
file changes. Advisory by default: do not add it to the required checks
and do not set `continue-on-error`. Keep only the audit steps for the
toolchains the project has; commands for other toolchains and the GitLab
shape are in `references/providers-and-stacks.md`.

```yaml
  security:                            # advisory until the team marks it required (Step 7)
    runs-on: ubuntu-latest
    timeout-minutes: <e.g. 10>
    steps:
      - uses: actions/checkout@<sha> # v7
        with:
          persist-credentials: false
          fetch-depth: 0               # full history: a key added then deleted in the PR still counts
      - name: Secret scan
        run: |
          docker run --rm -v "$PWD:/repo" -w /repo \
            <gitleaks-image>@sha256:<digest> \
            git --redact --verbose /repo
      - uses: actions/setup-node@<sha> # v7
        if: ${{ !cancelled() }}
        with:
          node-version-file: <.nvmrc or package.json>
      - name: Audit JS dependencies     # fails on high/critical, prints the rest
        if: ${{ !cancelled() }}
        run: <npm run audit, or: npm audit --audit-level=high>
      - uses: actions/setup-python@<sha> # v7
        if: ${{ !cancelled() }}
        with:
          python-version-file: <.python-version or pyproject.toml>
      - name: Audit Python dependencies # any known advisory fails; exceptions by ID, with a reason
        if: ${{ !cancelled() }}
        run: <make audit, or: pip install pip-audit==<x.y.z> && pip-audit -r <requirements exported from the lockfile>>
```

- `<digest>`: resolve the digest of the scanner's current release tag
  (`docker buildx imagetools inspect <image>:<tag>`), same rule as `<sha>`.
  `<x.y.z>`: the tool's current release, pinned exactly — or, better, the
  tool already sits in the project's dev dependencies and `make audit`
  calls it.
- The scanner subcommand (`git`), `--redact`, and each audit's severity
  flag are version-sensitive: check them against the pinned version's
  `--help` or current docs (context7) before writing. If the scanner
  reports a "dubious ownership" error on the mounted checkout, fix it the
  way the image's docs say for that version — do not drop to a tree-only
  scan.
- Scanner allowlist (e.g. `.gitleaks.toml` / `.gitleaksignore`) is a
  committed file in the repo: allow the paths that carry
  `docker-compose.test.yml`'s fixture values, never whole rules.
- No `Install` step: the audits read the lockfile (or its export), and
  nothing here runs project code.
