# The session's context — what it keeps, and when to hand over

Read at the start of every stage that dispatches agents or runs for long — `work`, `ui-design`, `screen-spec`,
`ui-test-cases`, `security-audit`, the design stages — and after a compaction. A session keeps everything it reads
until it ends, and every later call pays for all of it again. Measured on a real project: one session of document
stages kept 2.1 million characters of agents' reports (314 of them, 6,400 characters in the middle, up to 33,000)
and 0.8 million of shell output; a `work` session grew by ~100,000 tokens a unit. Near the host's limit the session
is compacted, and a compaction is where rules get lost.

## What the session lets in

- **Agents report short.** Every agent ends with its packet's report in about 2,000 characters and writes what is
  long — lists, evidence, reasoning, a file-by-file account — to a details file it names (`executor-catalog` →
  Dispatch contract → Short reports). The session reads that file only when the report asks for a decision, a
  status is not `DONE`, or the stage's own rule says so.
- **Checks run through `work/scripts/run_check.py <name> -- <command>`**: the full output to a log, a summary in
  the context (`work` → `references/run-hygiene.md` → What reaches the orchestrator).
- **Other long output goes to a file** — a search, a diff, a listing, a scanner's result: `> <file>`, then read the
  part needed. A document is read in the parts the step needs, not whole «to have it».

## When to hand over

At each safe boundary — a stage closed, one item of a long stage done (a screen drawn, a screen spec written, a
section of test cases, an audited area, a unit committed) — run
`python3 "${CLAUDE_SKILL_DIR}/../reflect/scripts/context_size.py" "$PWD"` (from another skill: the plugin's
`reflect/scripts/context_size.py`). Over 300,000 tokens (exit 2), hand over at that boundary:

1. Save where the stage stands: its progress file and `resume.md` (`references/pause-and-resume.md`), the next
   item named («продолжать с S-7»), anything decided in the chat that no document holds yet.
2. **Run by a parent session:** send it «<этап> <version> ПЕРЕДАН · после <item> · контекст <N> тыс. · продолжать
   с <item>» and stop (`references/parent-session.md`).
3. **No parent, and the host can start a session** (Claude Desktop: `mcp__ccd_session__start_session`, often
   deferred — load it with ToolSearch `select:mcp__ccd_session__start_session` first): start one locally, in this
   folder, with a fresh context and no worktree, titled «<version> · <stage> · часть <n>», prompt «продолжи
   <stage> <version>; родительская сессия — <this session>; по закрытии, остановке или передаче пиши ей». This
   session becomes its parent (`references/parent-session.md`).
4. **Neither:** one line to the user — open a new session in this folder and write «продолжи» — and stop.

The new session finds its place from git, the progress file and `resume.md` (`references/where-am-i.md`). Two
sessions working in one project at once: the script reads the newest and names it — check the name.
