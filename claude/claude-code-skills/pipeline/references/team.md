# Handing stages to other people

Read when the user hands a stage to another person — «отдать дизайн
дизайнеру», «ТЗ на экраны сделает аналитик» — and in any session of a
person who took one. One person, the **owner**, runs the pipeline and the
backend branch; each other person takes stages of the design branch and
runs them with the same plugin on their own machine, in parallel with the
owner.

Everyone works in the **iteration's branch** (`iteration/<version>`, made
from `main` when the iteration opened — `pipeline` → Service version). No
personal branches: each person writes only their stages' folders, so
commits never collide, and `git pull --rebase` before every push is all the
coordination the branch needs. `main` gets the iteration once, at the end.

## Who can take what

| Stage | Writes only | Needs on the iteration branch before it starts |
|---|---|---|
| `ui-design` (stage 7) | `documentation/ui/frames-register.md` (frames live in Figma) | the SRS |
| `screen-spec` (stage 8) | `documentation/ui/screen-specs/` | the frames register and the API |
| `ui-test-cases` write (stage 9) | `documentation/ui/test-cases/` | the screen specs |

One person may take several stages (a designer: mockups and test cases; an
analyst: the screen specs). The backend branch, the SRS, the API and
everything after stage 9 stay with the owner.

## Handing over (the owner's session)

1. At the fork after the SRS (`pipeline` → Two branches), or whenever the
   user asks, ask which stages go to whom: one question per person, the
   options the rows above. When the iteration's design owner is a designer
   with the plugin (`references/design-owner.md`), `ui-design` is theirs
   without asking; ask only about the other stages.
2. Make sure everything those stages read is committed on the iteration
   branch — the SRS, `ui-wishes.md`, the API when it exists — and give the
   push command (`git push -u origin iteration/<version>`); the plugin never
   pushes.
3. Write the hand-off text in the chat, ready to forward, one per person:
   clone the repository (or pull), install the plugin (README → Установка),
   `git switch iteration/<version>`, the Figma file link when the stage
   draws, and the command to start (`/dev-pipeline:ui-design`). Add which
   input is not there yet and who brings it («ТЗ на экраны начнёте, когда
   на ветке появится API»).

The owner goes on with the backend branch at once, and pushes each finished
document so the others can pull it.

## In a session of a person who took a stage

- **The version comes from the branch name.** `documentation/plans/` is out
  of git, so the folder is not there: create `plans/<version>/` from
  `iteration/<version>` and keep the progress files in it. Never open a new
  version, never switch to another branch.
- **Inputs come from the branch.** `git pull --rebase` before the stage
  starts; when an input the table names is not there yet, say what is
  missing and from whom, and stop — nothing here can replace it.
- **Write only the stage's folder.** A changed decision whose owner document
  lies outside it — the SRS, the API, the architecture — is not edited here
  (`references/decision-changes.md` stays the owner's): write it in the chat
  as a request to the owner, ready to forward («Нужно решение владельца:
  …»), mark the item `⛔ ждёт решения владельца`, go on with the rest, and
  pull once the owner has landed it.
- **Commit and share as you go.** Each finished screen, spec or section is a
  commit with only the stage's folder staged and no `version`, changelog or
  pin change (`doc-versioning` → Commits that are not stamps); after it,
  give the push command with `git pull --rebase` before it, so the others
  see the work as it lands. The stage's own gate (`doc-review` for screen
  specs) runs here, with this person answering.
- **Done** is the stage's own close plus one line for the owner, ready to
  forward: «<этап> готов и запушен в `iteration/<version>`: <что сделано>».
  No pipeline offer after it — the next stage belongs to someone else.

## The owner, when someone reports done

`git pull --rebase`, then check what came: the commits change only that
stage's folder; every screen spec has `reviewed:` or a named skip. Say who
can start now — the analyst once the frames are there, the designer's test
cases once the screen specs are — with the line to forward. The meeting
point (stage 10) waits until every handed stage is reported done.

## Where am I, with helpers

`git fetch`, then read the iteration branch on `origin`: the last design
stage present there and which handed stage is still missing its input.
Report the design branch from `origin/iteration/<version>`, not from the
local copy alone.
