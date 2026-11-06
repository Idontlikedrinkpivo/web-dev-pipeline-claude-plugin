# Several iterations without the user — and parent sessions

Read when the user asks for work to go on without them — «сделай итерации 1, 2 и 3
подряд», «работай сам, я занят другим проектом» — or starts other sessions to run
iterations one after another while this one waits. Without these two things a chain
stops on its first behaviour question and stays stopped, or a finished iteration
waits for the next one until the user notices. The last section, Keeping the
run moving, is for every long run, with the user away or not.

## Before the first iteration: the standing answers

One message, before anything starts, with every question the chain will meet and a
default for each, so the user answers once:

- **Behaviour questions from reviews** (a `STOP` on a design gap, a finding against a
  settled decision): stop that iteration and go on with the next one / take the
  recommended option and record it as a changed decision / stop the whole chain.
- **The gates** each iteration offers: which run without asking (`doc-review`,
  `plan-review`, `docs-consistency` are recommended), which are skipped.
- **The security audit** and **the UI-test run** at each iteration's end: run / skip /
  only at the last iteration. The audit's live check (Shannon, `security-audit` →
  `references/live-pentest.md`): skip / run when it is set up — skip when not asked, it spends
  the user's own model budget.
- **The e2e scope**: the whole suite / the areas the iteration touched.
- **Merge, tag and push**: the plugin never pushes; merge to `main` and tag each
  iteration as it closes / leave the branches for the user.
- **Dependency updates** a stage proposes: take patch and minor / ask later.
- **Stop conditions**: what stops the whole chain — a P0 security finding, data loss
  on a stand, a red suite after its fix rounds, a cost or time limit the user names.

Record the answers in the project's memory (the project's `CLAUDE.md` section or
the session's notes the project uses) and paste them into the packet or the first
message of every session the chain starts. A question the block did not cover
stops only its iteration, with the question saved in its `resume.md`; the chain
goes on where it can. One question per message still holds — this block is the
one sanctioned exception, a list the user answers once.

## While another session runs an iteration

- **The child says when it is done.** The session that runs an iteration sends one
  direct message to the waiting session when it closes — «ИТЕРАЦИЯ <version>
  ЗАКРЫТА · main <sha> · тег v<version>» — or when it stops — «ИТЕРАЦИЯ <version>
  ОСТАНОВЛЕНА · <причина>». Put that duty in the child's first message.
- **The waiting session checks, never answers from memory.** On each message from
  the user, and before saying anything about the chain, it checks the child's state —
  its task status, or `documentation/plans/<version>/summary.md` (the close) and
  `resume.md` (a stop) — and starts the next iteration as soon as the previous one is
  closed, without waiting to be asked. «Ещё идёт» is said only after that check.

## Parent and nested sessions

The chain runs through a parent session that opens each stage in a nested session —
`references/parent-session.md`. Without the user, a nested session's question goes to the parent as «ВОПРОС · …»:
the standing answers settle it, or that branch waits and the rest goes on.

## Keeping the run moving

Read by every long run (`work`, a UI test run, an audit), with the user away
or not — a chain of iterations only makes the cost of a stopped run higher.


A long stage runs while the user is away — asleep, in a meeting — so a turn
that ends with nothing running stops it for hours: nothing wakes the
session until the user writes again.

- **A turn ends only while the next step runs — or on a question that
  blocks it.** Until the last item is done, every turn ends with the next
  step already started — an executor, a reviewer, a check, dispatched in
  the background, whose completion wakes the session again. The one other
  way to end a turn is a question the run cannot go past without the
  user's answer — one of the stage's own stop cases (a missing decision, a
  review's `STOP`, rounds that stopped making progress): then nothing is
  started, the question is the end of the turn, and the row says
  `⛔ остановлено`. Never end a turn on prose alone, and never on
  «продолжаю…» without the call.
- **Call first, then write.** Start the next step, then write the chat
  line (After each item). Text written before the call can be cut off —
  a dropped connection, a stream that ends mid-sentence — and the call
  after it is lost with it; text after the call costs nothing if it is
  cut. A blocking question has no call after it, so it is simply the last
  thing in the turn.
- **A message that is not a decision does not stop the run.** A stray
  keystroke, «ну?», «ты тут?», a question about progress: answer in one
  line with the count and the link, and go on. Only a stop («стоп»,
  «подожди», «остановись») or a changed decision changes the run — the
  latter through `pipeline` → `references/decision-changes.md`.
- **Check, don't ask, when a run can find out.** Before a question to the
  user inside a run (`work`, a UI test run, an audit), sort it: a fact the
  session can observe by running something — which port the stand uses,
  whether the API returns a field, whether a test passes without the fix,
  whether a failure is the app's or the test's, whether a library supports
  a call — is not the user's to answer: run the check and record it as
  «решил по проверке: <что запустил> → <результат>». Only a decision —
  product, scope, a rule the documents leave open, a finding against a
  settled decision — goes to the user. The design stages ask their
  questions on purpose and are not affected.
- **Pause and pick up through the resume note.** A long run keeps
  `resume.md` beside its progress file and reads it first when it resumes
  (`references/pause-and-resume.md`).
- **Never ask whether to continue.** The run was agreed when it started; it
  asks only in its stage's stop cases. A turn that finds the run idle — the
  last one was cut off, the session was compacted, the user wrote into a
  silence — rebuilds the rows from disk and git and starts the next step
  at once, saying in one line that it resumed.
