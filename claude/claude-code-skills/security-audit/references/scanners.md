# Scanners

Read in Step 1. Each scanner runs from the repository root through its
Docker image, so nothing is installed on the machine. Pull the image once
per audit, check its flags with `--help` before relying on the commands
below (tools rename subcommands between majors), and save the raw output
under `OUT=$(git rev-parse --git-dir)/pipeline-work/security`. Never paste
raw output into the chat or a packet: the auditor reads the file.

## Dependencies — `osv-scanner`

Known vulnerabilities in the versions the lockfiles pin
(`package-lock.json`, `pnpm-lock.yaml`, `yarn.lock`, `uv.lock`,
`poetry.lock`, `requirements*.txt`).

```bash
docker run --rm -v "$PWD:/src" ghcr.io/google/osv-scanner:latest \
  scan source -r /src --format json > "$OUT/osv.json"
```

Without Docker: `npm audit --json` / `pip-audit -f json` (or `uvx
pip-audit`). Exit code 1 means "found something", not a failure.

Reading it: a vulnerability counts against the app only when the package
ships to production (not a dev dependency) **and** the vulnerable function
is reachable from this code — the auditor checks the second part. A fixed
version, when the advisory has one, is the fix in words.

## Secrets — `gitleaks`

Keys, tokens, passwords, private keys in the working tree **and in every
commit**: a secret deleted in a later commit is still in the history and
still has to be rotated.

```bash
docker run --rm -v "$PWD:/repo" ghcr.io/gitleaks/gitleaks:latest \
  git /repo --report-format json --report-path /repo/.git/pipeline-work/security/gitleaks.json --redact
```

`--redact` keeps the secret's value out of the report. Older majors spell
the subcommand `detect --source /repo`. Fixture values the test compose
file declares on purpose (`deploy-topology` → Step 6) are not findings;
anything else that looks live is P0 until the user says it is a dummy.

## Patterns — `semgrep`

Code patterns of the OWASP Top 10 and the stack's own pitfalls.

```bash
docker run --rm -v "$PWD:/src" semgrep/semgrep:latest \
  semgrep scan --config p/owasp-top-ten --config p/<stack> \
  --json --output /src/.git/pipeline-work/security/semgrep.json /src
```

`<stack>`: `p/typescript` and `p/react` for a TypeScript project,
`p/python` for Python; one `--config` per pack. Exclude generated code,
`node_modules/`, test fixtures and `documentation/` with `--exclude`.

Reading it: semgrep matches shapes, not data flow. A raw SQL string built
from constants is not an injection; the auditor follows each hit to see
whether outside input reaches it.

## Docker images — `trivy` (in `deploy-topology`, not here)

The built images exist only in `deploy-topology` Step 8, so the image scan
runs there, over the release tar:

```bash
docker run --rm -v "$PWD/release/<version>:/r" aquasec/trivy:latest \
  image --input /r/<project>-<version>.tar --severity HIGH,CRITICAL --format json
```

## When a scanner cannot run

No Docker and no local tool, no network for the rule packs, an image that
will not pull: write the row `⚠️ не запускался: <причина>` and name it in
the verdict line. The audit still runs its trace; the gap is the user's to
see, not the audit's to hide.
