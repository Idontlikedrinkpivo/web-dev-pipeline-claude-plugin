# The project's verify skill

Read in Step 7a, and by any stage that is about to run the app and finds no
`.claude/skills/verify/` in the project (`ui-test-cases` mode run, a browser
suite in `work`). `security-audit` only reads its Traps when it exists — its
scanners need no running app — and never writes it. Adapted from pstack's
`create-verification-skill` / `maintain-verification-skill`.

## Why it exists

Every run that drives the app — a UI acceptance run, an e2e suite, the
operations document's proof — starts by working out the same things: the launch
command, when the stand is really ready, how to sign in per role, which
traps this environment has, how to leave the machine as it was. What one
session works out dies with it, and the next one pays again, or fails on
the same trap. A project-local skill keeps that knowledge in the
repository, next to the code it describes.

Its worth is reliability, not speed. On a healthy, warm stand a capable
agent finds its way without it. It pays when the stand is broken in a way
the code does not show — a database migrated from other code, a build older
than the commit, a port held by another stand — and when a run must not
damage the owner's state (their reports, their screenshots, their stand).
Measured on a real project, 2026-10-14: the doctor caught a stand that could
not start at all; a run without the skill overwrote the owner's test report.

## What it is

`.claude/skills/verify/` in the project root (in a monorepo, in the package
that has the stand), committed with the test topology:

```text
.claude/skills/verify/
  SKILL.md            frontmatter name: verify, a description naming the app, the stand and when to read it
  scripts/doctor.sh   read-only check: exit 0 = drive it, 1 = fix what it names first
  scripts/token.sh    a bearer token per test role, in any sign-in mode (when the app has sign-in)
  features/README.md  the feature map: one row per user-facing feature
  features/<feature>.md
```

It is written for an agent arriving cold, in English, with every command
taken from the repository — never a placeholder, never an example from
elsewhere. Where a line was not run, it says «unverified».

## SKILL.md sections

- **Launch** — the exact command that starts the test stand from what is
  on disk (the project's `make up-test` or the compose command), how to
  switch modes the app has (sign-in modes, feature flags), what the target
  leaves running and what it removes.
- **Ready means usable** — the condition that makes the stand worth
  driving: `/health/ready` answers 200, migrations applied, the mode
  answered — not «the container is healthy».
- **Doctor** — how to run it and when: before the first drive, after
  anything surprising, after a failed drive.
- **Drive** — the browser runner and how to select one case safely (the
  exact filter syntax that does not match neighbours), API calls as a role,
  roles and their accounts, where test data comes from, and the difference
  between a role in the auth fixture and a right in the app's database.
- **Evidence** — where each kind of proof lands, and how to keep a trial
  run's output apart from the owner's: the report and results folders, the
  screenshot folder, any shared state (token caches, rate-limit records)
  and the environment variables or the copy that redirect them.
- **Cleanup** — record which services were running before; stop only what
  the run started; never remove the stand's volumes; never touch another
  stand (dev, demo); stop every watcher; evidence stays. End by comparing
  the end state with the start.
- **Traps** — every environment fault met so far, each with its symptom,
  its cause, its fix, which fixes need the owner's yes (anything that
  changes shared data), and **the live command that shows whether it is
  there now** (`docker pull alpine:3.20`, `curl -sI <source>`, `lsof -i :<port>`);
  a trap that can be checked automatically is also a doctor line. A trap is a
  hypothesis until its command fails: a run checks it before stopping or
  deferring a unit for it, and a trap whose command passes is removed in the
  same run (`work` → `references/run-hygiene.md` → The environment). This
  section grows: a run that meets a new trap adds it, with its command, before
  it finishes.

## The doctor

A shell script, read-only, one line per check, `READY` / `NOT READY` and an
exit code. It checks at least:

| Check | Why |
|---|---|
| each service of the test stand is up and healthy | the obvious one |
| the stand's port is owned by this stand's container | another stand on the same port answers the tests |
| `/health/live` and `/health/ready` answer 200 | readiness covers the database and storage |
| the mode the app reports (sign-in mode, flags) | cases that need the other mode skip silently |
| the database schema the app expects exists | the app does not create it; a renamed schema stops `migrate` |
| every migration recorded in the database exists in this checkout | a database migrated from other code fails later with «already exists» |
| the running **image** is not older than `HEAD` | a container recreated from an old image looks fresh; check the image |
| the host tests' database (`TEST_DATABASE_URL`) is not the stand's database | host tests drop and rebuild their schema; on the stand's database they wipe its data |

Room-booking, for shape only:

```text
postgres   Up 2 hours (healthy)
backend    Up 3 minutes (healthy)
frontend   Up 3 minutes (healthy)
db schema  room_booking present
migrations 5 recorded, all in this checkout
port 8080  room-booking-test-frontend-1
/health/live   200
/health/ready  200
build      backend image 2026-10-14T09:12 UTC, HEAD 2026-10-14T09:05 UTC
test db    room_booking_test_host ≠ stand room_booking_test
READY
```

## The feature map

`features/README.md` lists the user-facing features with their screen ids,
spec files and a link to one file per feature. Each file has four parts:
sub-features; how a user gets there; how to drive it (API operations,
specs, helpers); gotchas met so far. Start with the three to five features
the project's use cases name first; a run that needs another adds it.

## Writing it

1. **Read the repository, not the user.** Compose files, the Makefile or
   package scripts, the test runner's config and helpers, the auth
   fixtures, the readiness code, the last run reports in
   `documentation/plans/` (their notes on what went wrong are traps).
2. **Write the files.** Every command from the repository.
3. **Prove it — required.** Run it as written: record the stand's state,
   launch, doctor until `READY`, a token for one role and one API call,
   one case of one mapped feature in the browser with its output kept
   apart from the owner's, then cleanup back to the recorded state. A
   skill that was never run end to end is a draft. A fault the proof meets
   becomes a Trap and, when it is a stand fault, a doctor check; a fix that
   changes shared data waits for the owner's yes. In `deploy-topology`
   the stand's proof (Step 7b: the service check in the container, the
   resource measurement) runs on the stand this proof brought up, before
   the cleanup (`deploy-doc.md` → The stand's proof).
4. **Record the proof** in SKILL.md's opening lines: the date, the commit,
   what ran and what it produced.
5. **Commit it alone** (`test(e2e): скилл запуска стенда`), only the
   `.claude/skills/verify/` folder — never other files under `.claude/` —
   with the trailer `Plan-Unit: <version>/verify-skill`, so a whole-run review
   whose range holds it (written for a browser suite in `work`) maps it
   instead of flagging an unknown commit (`code-review-full` → Step 1).

## Using it

A stage that runs the app reads SKILL.md, runs the doctor before the first
drive and after every surprise, follows Launch, Evidence and Cleanup, and
adds a Trap for anything new before its last line. A trial or a partial run
keeps its output apart from the owner's; a full acceptance run is the
owner's record and may replace it.

## Keeping it honest

Each iteration, in `deploy-topology` Step 7a — the stage runs after `work`
and the UI acceptance run, when the stand last changed: run the doctor and
one drive per feature the iteration changed; fix what
drifted (a command, a path, a role); add the iteration's new features to
the map; commit the corrections alone. A behaviour the map describes that
the app no longer has is either the map's drift (fix it) or the app's
regression (report it, never paper it over in the map).
