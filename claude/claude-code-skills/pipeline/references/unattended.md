# Several iterations without the user

Read when the user asks for work to go on without them — «сделай итерации 1, 2 и 3
подряд», «работай сам, я занят другим проектом» — or starts other sessions to run
iterations one after another while this one waits. Without these two things a chain
stops on its first behaviour question and stays stopped, or a finished iteration
waits for the next one until the user notices.

## Before the first iteration: the standing answers

One message, before anything starts, with every question the chain will meet and a
default for each, so the user answers once:

- **Behaviour questions from reviews** (a `STOP` on a design gap, a finding against a
  settled decision): stop that iteration and go on with the next one / take the
  recommended option and record it as a changed decision / stop the whole chain.
- **The gates** each iteration offers: which run without asking (`doc-review`,
  `plan-review`, `docs-consistency` are recommended), which are skipped.
- **The security audit** and **the UI-test run** at each iteration's end: run / skip /
  only at the last iteration.
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
