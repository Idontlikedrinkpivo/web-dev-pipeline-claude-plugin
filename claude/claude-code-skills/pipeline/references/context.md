# The session's context — what it keeps, and when to hand over

Read at the start of every stage that dispatches agents or runs for long — `work`, `ui-design`, `screen-spec`,
`ui-test-cases`, `security-audit`, the design stages — and after a compaction. A session keeps everything it reads
until it ends, and every later call pays for all of it again. Measured on a real project: one session of document
stages kept 2.1 million characters of agents' reports (314 of them, 6,400 characters in the middle, up to 33,000)
and 0.8 million of shell output; a `work` session grew by ~100,000 tokens a unit. Near the host's limit the session
is compacted, and a compaction is where rules get lost. Right after one, the session-start hook prints the rules
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

## When to hand over

At each safe boundary — a stage closed, one item of a long stage done (a screen drawn, a screen spec written, a
section of test cases, an audited area, a unit committed) — measure the context:

- **The measure.** In Claude Desktop (the session tools exist): `mcp__ccd_session_mgmt__get_usage` with
  `session_id` `self` (often deferred, load it with ToolSearch) — `tokensUsed`, `contextWindow`, `percentUsed`,
  `autoCompactsAtPercent`. It reads this session's own process, so two sessions in one project cannot measure each
  other. Only where there is no such tool (a terminal):
  `python3 "${CLAUDE_SKILL_DIR}/../reflect/scripts/context_size.py" "$PWD" --next high|mid|low [--session <own id>]`
  (from another skill: the plugin's `reflect/scripts/context_size.py`); it reads `context_limit` from the same file
  below and cannot see the window (exit 2 — hand over, exit 0 — go on).
- **The hand-over point** is the lower of two numbers: `context_limit` in the project's
  `documentation/.dev-pipeline.json` — the cost limit, since every call pays for the whole context (an integer,
  tokens, optional; 300,000 when absent) — and four fifths of where the app auto-compacts
  (`autoCompactsAtPercent` / 100 × `contextWindow` × 0.8). A 1,000,000-token window: 0.97 × 1,000,000 × 0.8 ≈
  776,000, so 300,000 wins; a 200,000-token window: 0.97 × 200,000 × 0.8 ≈ 155,000 wins. The rule fits any window
  without a setting.
- **Hand over when** `tokensUsed` plus what the next item usually takes — a High unit 120,000, a Mid 70,000, a Low
  35,000; a screen, a screen spec or an audited area counts as Mid — crosses that point: at that boundary, at once
  and without the user. Either way the context is never a reason to pause, stop or ask (the user, 2026-11-04).
  Below it — go on.

To hand over:

1. Save where the stage stands: its progress file and `resume.md` (`references/pause-and-resume.md`), the next
   item named («продолжать с S-7»), anything decided in the chat that no document holds yet.
2. **Run by a parent session:** send it «<этап> <version> ПЕРЕДАН · после <item> · контекст <N> тыс. · продолжать
   с <item>» and end the turn. The parent clears this same session and starts it again with «продолжи с <item>» — no
   new session (`references/parent-session.md` → What comes back). The send's result «delivered» (the parent's turn
   started) or «queued» (it waits behind the parent's current work) are both fine; anything else is an error — the
   parent archived, the message refused or held for approval — and then the session does not wait: it goes on in
   place, as after «продолжай здесь». On «продолжай здесь» (the clear was refused) go on in this session and do not
   hand over again in this stage: the host compacts it, and the session-start hook prints the stage's rules back. A
   parent and its nested sessions run in one permission mode: a session in another mode holds cross-session
   messages for the user's approval, which silently stalls the chain, so the parent never changes one session's
   mode alone.
3. **No parent, and the host can start a session** — a session the pipeline should have run from a parent
   (`references/parent-session.md` → Which one am I): go on in this session, no new one — the host compacts it, and the
   session-start hook prints the stage's rules back. A new session opened on the way needs the user's click on a
   card and stops an autonomous run (the user, 2026-11-02).
4. **Neither (a terminal):** go on in this session, as in step 3 — the host compacts it, and the session-start hook
   prints the stage's rules back. The user may at any time run `/clear` themselves and write «продолжи»; the session
   then picks up from `resume.md` and git. Stopping for the context is never right (the user, 2026-11-04).

A cleared or new session finds its place from git, the progress file and `resume.md` (`references/where-am-i.md`). Two
sessions working in one project at once matter only to the script (the app's tool reads its own session): without
`--session` it reads the newest and names it — check the name.
