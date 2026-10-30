# Several iterations without the user — and parent sessions

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

## Parent and nested sessions

When the user opens a session to run work through nested sessions — «веди итерацию 2.2.0 через вложенные
сессии», «сделай итерации 1–3, я загляну утром», or a run hands over at its context limit (`work` →
`references/run-hygiene.md` → Context) — this session is the **parent**:

- **It runs no stage itself.** It collects the standing answers (above), opens nested sessions, reads their
  short messages, relays questions, and decides what comes next. Its context grows only by those messages.
- **A nested session** is opened with the host's session tool — Claude Desktop: `start_session`, a fresh context,
  no worktree — so it shows under the parent in the sidebar and the user can open it and talk to it. Its prompt:
  the task («продолжи прогон 2.2.0», «открой итерацию 2.3.0 и начни с brainstorm»), the standing answers, the
  parent's name, and the duty to report. Its title: «<version> · <stage or часть n>».
- **What a nested session sends the parent**, one line each: «ИТЕРАЦИЯ <v> ЗАКРЫТА · main <sha> · тег v<v>»;
  «ПРОГОН <v> ПЕРЕДАН · после U<n> · контекст <N> тыс. · продолжать с U<m>»; «ОСТАНОВЛЕНА · <причина>»;
  «ВОПРОС · <the question with its options>» — and it waits for the answer.
- **What the parent does on each:** closed → the next stage or iteration, in a new nested session; handed
  over → a new nested session «продолжи прогон <v>» (it starts from git, repeats nothing); stopped → tell the
  user; a question → the standing answers settle it, or the user is asked and the answer goes back to that
  session (`SendMessage`), or, with the user away and no standing answer, that branch waits and the rest goes on.
- **No session tool** (a terminal, another host): the parent tells the user, one line each time, to open a new
  session in the folder with the prompt it gives — the same chain, by hand.
- **Before answering about the chain**, the parent checks each nested session's state (its status, the
  iteration's `summary.md`, `resume.md`) — never from memory.

