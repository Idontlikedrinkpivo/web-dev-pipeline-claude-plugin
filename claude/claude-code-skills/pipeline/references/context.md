# The session's context — what it keeps, and where it is compacted

Read at the start of every stage that dispatches agents or runs for long — `work`, `ui-design`, `screen-spec`,
`ui-test-cases`, `security-audit`, the design stages — and after a compaction. A session keeps everything it reads
until it ends, and every later call pays for all of it again. Measured on a real project: one session of document
stages kept 2.1 million characters of agents' reports (314 of them, 6,400 characters in the middle, up to 33,000)
and 0.8 million of shell output; a `work` session grew by ~100,000 tokens a unit. At its auto-compact window the session is
compacted, and a compaction is where rules get lost. Right after one, the session-start hook prints the rules
of the stage the session ran last (`references/keep-after-compaction.md`, by `scripts/keep_rules.py`); a changed
key rule of a stage changes its section there too.

## What the session lets in

- **Agents report short.** Every agent ends with its packet's report in about 2,000 characters and writes what is
  long — lists, evidence, reasoning, a file-by-file account — to a details file it names (`executor-catalog` →
  Dispatch contract → Short reports). The session reads that file only when the report asks for a decision, a
  status is not `DONE`, or the stage's own rule says so.
- **Checks run through `work/scripts/run_check.py <name> -- <command>`**: the full output to a log, a summary in
  the context (`work` → `references/run-hygiene.md` → What reaches the orchestrator).
- **Other long output goes to a file** — a search, a diff, a listing, a scanner's result: `> <file>`, then read the
  part needed. A document is read in the parts the step needs, not whole «to have it».

## Compaction

The host compacts the session when the context reaches its auto-compact window; the session never stops, pauses,
asks or hands over for the context. Three ways to free a session's context were tried live and two failed: a
session cannot compact itself, a parent's «/compact» arrives as plain text, and a parent's `clear_session` of a
nested session was refused by the auto-mode classifier (ai-initiatives 2.3.0, 2026-11-17) — so the run stopped at
«готово к /compact» and waited for the user. The host's own compaction kept the same session going eight times in
that run; the user chose compacting over clearing (2026-11-17) and no pauses (2026-11-04, 2026-11-18).

- **The window.** A 1M-token model compacts at about 967,000 tokens by default, and every call pays for the whole
  context. The pipeline wants it at `context_limit` — the cost limit in the project's
  `documentation/.dev-pipeline.json` (an integer, tokens, optional; 300,000 when absent). Before the first nested
  session of an iteration — or, without a parent, before a long stage's first item — read the session's window
  (`mcp__ccd_session_mgmt__get_usage` on `self`, often deferred: load it with ToolSearch): `contextWindow` above
  `context_limit` means nothing lowers it yet. Then ask once, in chat: «Сжимать контекст на <N> тыс.? Запишу
  `"autoCompactWindow": <N>` в `.claude/settings.local.json` проекта — новые сессии будут сжиматься на этом
  пороге». On a yes, merge that key into the file (create it with `{}` when missing; keep its other keys); a session
  already running takes the window only from `/autocompact <N>k` typed in its own window — say so for those still
  open. On a no, go on: the run is the same, only dearer. It is the user's setting: never write it without the yes,
  never in `~/.claude`.
- **Compaction waits for a boundary in `work`.** The plugin's `PreCompact` hook (`hooks/compact-hold.py`) holds an
  automatic compaction of the session that runs `work` while a unit is in flight — a row of
  `plans/<version>/progress.md` neither «⏳ ждёт» nor «✅» — and the host skips it and tries again later, so it lands
  after the unit's commit. The hold stops at `context_limit` + 150,000 and on a model without the 1M window; past it
  the compaction goes through mid-unit, and the step lines in `resume.md` carry the unit on (`work` →
  `references/run-hygiene.md` → Context). Each decision is a line in `plans/<version>/.progress-compact.log`. Other
  stages compact where the host decides; their items are short and each ends written to disk.
- **Any moment must be safe to compact**, since the hold has a cap and other stages have none: what the chat settled
  goes to its file at once — the progress file, `resume.md` (`references/pause-and-resume.md`), the stage's report,
  a decision into its document (`references/decision-changes.md`) — never «at the end». The hook also tells every
  compaction what its summary keeps (the stage, the item and its step, decisions not yet on disk, rules the user or
  the parent gave this session).
- **After a compaction** the session-start hook prints the stage's rules (`references/keep-after-compaction.md`); the
  session takes its place from git, the progress file and `resume.md` (`references/where-am-i.md`), not from the
  summary — a unit listed in flight is still running: wait for it, never send it to a second executor.
- **The user may compact or clear at any time** (`/compact`, or `/clear` and «продолжи»); the session picks up from
  the same files. A `/compact` the user types is never held.

`reflect/scripts/context_size.py` reads a session's size from its transcript where the app's tool is absent (a
terminal); it decides nothing.
