# Service version and the iteration

Read when a stage opens an iteration (it is the first to commit or to write
into `documentation/plans/`), when `plan` re-checks the level, and when a
question about versions, the iteration branch or `plans/` comes up.

## The number

The service has one number, `MAJOR.MINOR.PATCH`: the manifest's `version`,
the name of `documentation/plans/<version>/` (the iteration's plan, reports,
summary), the git tag `v<version>` that closes the iteration — the
**baseline**, the documents and code of that release — and the prefix of
the image tag `deploy-topology` writes. A document's `version` is the
release it last changed in (`doc-versioning` → What a version is).

| Level | When | Who decides |
|---|---|---|
| MAJOR | a big new capability that really extends the service: a new functional area, a new kind of user, a new way of working with it | the owner. Propose it when the iteration adds a new capability group (a new area) to the SRS, or the owner called the change big; the owner confirms |
| MINOR | new functionality inside existing areas: scenarios, screens, operations, fields | computed: at least one change typed «добавляет» or «ломает» in a versioned document |
| PATCH | fixes only: behaviour brought to what the documents already say | computed: only «уточняет» changes and code fixes |

A «ломает» alone makes a MINOR, not a MAJOR. Before the first release
versions are `0.x.y` (a manifest with no version → `0.1.0`); the owner says
when the first release, `1.0.0`, is.

## Opening the iteration

**The iteration opens at its first stage that commits anything or writes
into `plans/`** — `brainstorm` writing the business requirements, else
usually `srs-writer`, else `docs-consistency` or `plan`; a stage taken over
from someone else reads the version from the branch name
(`references/team.md`). An open `plans/<version>/` (no `summary.md`) is the
current iteration, and every later stage reuses it — it opens nothing.

1. **The number.** Greenfield: `0.1.0`, without asking. Otherwise propose
   the number after the manifest's, with its level and a one-line reason
   («MINOR: новые UC-5, UC-6 в бронированиях»), as one question
   (`references/question-format.md`):
   `A. <версия> (рекомендую)`, `B. Остановиться`, or the user's own number.
2. **Open it:**
   `python3 "<pipeline skill folder>/scripts/open_iteration.py" <version>`
   from the project's root. It updates `main` from `origin` when there is a
   remote, creates or switches to `iteration/<version>`, creates
   `documentation/plans/<version>/`, puts `documentation/plans/` into
   `.gitignore` (untracking it in its own commit), and prints what to say
   next. Exit 2 is a question for the user, never something to work
   around: the message names the options — an earlier iteration branch
   not merged into `main` (merge it first, start from `main` anyway with
   `--allow-unmerged`, or start on top of it with `--base`), or another
   iteration already open (`--allow-open`). Exit 3: not a git repository —
   ask, then `--init`. A working tree whose changes conflict with the new
   branch: ask how to handle them, never stash on your own.
3. **Who runs the design.** A product with screens is asked once, right
   after the number (`references/design-owner.md`); the script's `Design:`
   line says whether to ask. The stages that follow build on the answer.
4. **Code changes the plugin still wants** — when the script names them,
   say so in one line: `upgrade-code` makes them now, or `plan` makes them
   the iteration's first unit.

Every stamp of the iteration writes that number.

## One branch per iteration

Every stage of the iteration, by everyone who works on it
(`references/team.md`), commits on `iteration/<version>`; nothing is
committed to `main` during the iteration. Only that branch is pushed — the
plugin gives the command, the user runs it — and `main` receives the
iteration once, at the end, when the user merges it on GitHub. A stage
that finds itself on another branch with an open iteration runs
`open_iteration.py` with that version: it only switches.

## The level, re-checked

`plan` re-checks the level once every change is known, from the
iteration's typed changes: its changelog rows, plus any change not stamped
yet, typed the same way from the diff since the last tag. A changed level
is asked again; on a yes the session renames the open folder and replaces
the old number in that iteration's `version` fields, rows and pins in one
commit (`docs: итерация <old> → <new>`), and renames the branch to
`iteration/<new>` (`git branch -m`; the push command removes the old remote
name too) — it was never released, so nothing outside the iteration names
it. The plan's last unit bumps the manifest's `version` to the folder's
name — only when the manifest says otherwise: a new repository's scaffold
already wrote it, and a fix plan (`plan` `MODE fix`) never adds one
(`plan` → `references/modes.md`); `summary.md` and the tag close the
iteration (`pipeline` → End of the pipeline).

## Plans stay out of git

`documentation/plans/` is in `.gitignore`: the plan, its review, progress
files, stage reports and `summary.md` are working files on this machine;
git keeps the code, the contract documents, a `Plan-Unit:` trailer per unit
commit and the tag `v<version>`. `open_iteration.py` keeps the ignore line;
no stage stages a file under `plans/`. A fresh clone therefore has no
`plans/`: the tags name the closed iterations and the trailers since the
last tag the units already landed (`scripts/where_am_i.py` prints both).

## The API's own version

Called only by the project's own client, the API has no separate number:
`info.version` is the service version. With external consumers (Full
trigger "versioned partner API") it has its own SemVer and its major in the
path — `openapi-spec-generator` → Contract version.
