# Branch order

Read at the fork after the SRS (`pipeline` → Two branches) and whenever the
user changes the order mid-iteration. The two branches need different
inputs — the design branch only the SRS, the backend branch the SRS and
what it writes itself — so any order is correct, and the order is the
user's choice, asked once.

## The question

One question, these options, in this order (drop the ones that do not
apply — a product without screens has no design branch and no question):

- **Обе ветки параллельно** — both run in this session; see below.
- **Последовательно: сначала бэкенд, потом дизайн.**
- **Последовательно: сначала дизайн, потом бэкенд.** `ui-design` first;
  `screen-spec` waits for the API, so after the mockups the backend runs,
  then the screen specs and the test cases.
- **Только бэкенд** — the design branch is someone else's
  (`references/team.md`) or later.
- **Только дизайн** — the backend later.
- **Остановиться.**

Recommend from the situation, not from habit — first from who runs the
design (`references/design-owner.md`): «только бэкенд» when a designer
with the plugin takes the design branch, «сначала бэкенд» when a designer
draws by hand; «параллельно» when one
person runs both and the design work is small (edits to existing frames);
«сначала бэкенд» when the design is large and the user wants to answer one
branch's questions at a time. Say in one sentence why.

The answer sets the order for the iteration. Each stage still runs its
gates and still asks its transition (`pipeline` → Asking before a
transition), with the recommended option the next stage of the chosen
order; the user may change the order at any of those questions.

## Both branches in one session

- **Start both.** Dispatch the first stage of each branch; the long work
  (writers, Figma builders) runs in the background, so neither branch
  waits on the other.
- **Every question names its branch** — the chat line starts with
  `[Бэкенд]` or `[Дизайн]` — and questions still come one at a time: a
  question of the other branch waits until this one is answered, while
  that branch's background work goes on.
- **Separate files, separate commits.** Each branch writes only its own
  folders, so its stage commits never touch the other's; commit each stage
  when it closes, not both together.
- **Progress** — each stage keeps its own progress file and link
  (`references/progress-files.md`); the report after each step names the
  branch.
- **`screen-spec` waits for the API**, as in any order: when the mockups
  close first, the design branch pauses with that said, and resumes when
  `openapi-spec-generator` closes.
- **The meeting point** is unchanged: stage 10 starts when both branches
  are done.

## Only one branch

The other branch is not run in this session. When it is someone else's,
the hand-over follows `references/team.md`, and the meeting point waits for
their «готово и запушено». When it is later, the meeting point offers it
as the next stage.
