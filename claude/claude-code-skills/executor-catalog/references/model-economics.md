# Model economics behind the catalog

Read this before re-pointing a tier, adding a row, or when someone asks why an
agent file holds the alias it does. Dispatching a row does not need it. A
row's model and effort are the `model:` and `effort:` lines of
`_agents/<name>.md`; nothing else in the system names them. When you re-point
a file, check that this page still reads true and fix it in the same edit.

Claude Code accepts `haiku`, `sonnet`, `opus`, `fable`, or a full model id
such as `claude-opus-5-5`; effort is the agent file's own `effort:` field
(`low`, `medium`, `high`, `xhigh`, `max`), never a suffix on the alias.
Re-check an alias against `claude --model` whenever you touch a `model:` line.

## The three rules, in order

1. **No OpenAI models.** A standing policy for this system, not a quality
   judgment. Do not reintroduce a `gpt-*` slug when re-pointing a tier, even
   as a temporary substitute for a rejected one. A request to remap a tier to
   one is refused, not treated as a one-off preference.
2. **Code output stays on Sonnet**, except grade 0. See below.
3. **A reviewer is not the implementer's alias.** See below.

## Code output is Sonnet, grade 0 is Haiku

The grade rows `work` dispatches are `sonnet`: `impl-lite`, `impl-medium`,
`impl-hard`, and `impl-critical`. Writing a unit and applying a review fix
that needs judgment are the long output, so both stay on that one alias.

`mechanical-worker` — grade 0 and mechanical review fixes — is `haiku`
since 2026-10-07. Measured on a four-unit mechanical plan (a rename across
code and tests, a config reader with its test, `.env.example` and README,
the manifest version), two runs per model: Haiku 5.5 landed commits
byte-identical to Sonnet 5.5's, tests green, each unit in its own commit
with only its files, at about $0.02 against $0.30 for the row. Its work is
the cheapest to check — the session's own check and the tests confirm it —
and a unit that turns out to need a decision returns `BLOCKED` and goes one
tier up to `impl-lite`, on Sonnet. `haiku` means Haiku 5.5 from Claude Code
2.1.293; an older CLI maps it to Haiku 4.5, which was never measured on
code — update the CLI. A grade still changes the packet, which review roster fires, and the
effort (`low` for grade 0, `medium` for Low, `high` above); it does not
change the model. Escalation is a fresh dispatch with the previous report,
not a stronger alias: `impl-critical` keeps `impl-hard`'s model and effort.

`impl-ui` is `sonnet`, like every other code row. In the 2026-10-01
benchmark (one screen, six runs per model) Sonnet matched Opus on behaviour
and scored 4.1 against 4.4 of 5 on fidelity to the Figma frame, mostly
fonts and weights, at about 2.3 times lower cost. A retry stays on
`impl-ui`. Its review is the grade's `opus` review row, which also catches
visual drift against the frame.

`code-explorer` is `haiku`. It never edits. Beyond grade 0, Haiku is not a
code implementer: a unit with a decision in it is Sonnet.

## Code review is Opus

Code review is `opus` on `review-medium`, `review-hard`, and
`review-full-plan`. Review output is the short part (findings, not a
rewrite), and the reviewer must not be the alias that wrote the diff. Do not
move a code-review row to `sonnet` to save the dispatch — that is the
implementer reviewing its own diff. Grades still decide the roster (a Low
batch, a Mid pass, a High pass plus the risk pass, and one whole-run pass).
They do not pick a cheaper reviewer. `plan-review-hard` and `doc-review-hard`
share `opus` on their own packets.

`security-auditor` is `opus` at `high`, like the whole-run review: it
reads the code that exists, not a diff, and a missed hole is the expensive
failure. Scanners do the cheap, exhaustive part first, so the auditor reads
routes and access checks, not every file. Not measured.

There is no second whole-run pass. In the 2026-10-01 benchmark a second pass
on Opus or Fable found nothing the first pass had missed (9 of 9 planted
defects found by the first pass alone) and made the whole-run review 1.5–2
times as expensive, so it was removed.

The structural passes — `plan-review-medium` and `doc-review-low` — are
`sonnet`, like `doc-review-medium`. They were `haiku` until 2026-10-02: haiku
kept answering in free prose instead of the required findings format and
raised unmeasured P0s on plans; a structural check that the orchestrator
cannot read reliably is not cheap. That was Haiku 4.5; Haiku 5.5 was not
measured on review. `haiku` is on `code-explorer` and `mechanical-worker`
only.

`docs-consistency-checker` is `sonnet` at `high`. It reads the whole
document set and writes short findings, so input is the volume and Sonnet
carries it; `high` because a contradiction between two documents is found
by holding both in mind, not by matching text. Not measured; raise it to
`opus` only after a missed P0 on a real set.

`screen-writer` is `sonnet` at `high`: it reads frames and the contract and
writes long, exact tables; the decisions were made on the frames.
`ui-test-writer` (`medium`) and `ui-test-runner` (`high`) are `sonnet`:
cases are transcription from the documents, and the runner writes test
code, which stays on the code alias. Not measured.

## Writers: Sonnet and Opus — printed by Sonnet

Design and plan writers: Low is `sonnet`, Mid is `opus` at `high`, High is
`opus` at `xhigh`;
`srs-author` is `sonnet`. There are at most three writer dispatches per
greenfield run. A long contract's output tokens are the expensive part, so
the file is printed by `doc-typist` on `sonnet`, nested after the decisions
exist. Haiku stays off that row. Measured 2026-10-07 with a blind audit of
each print against its packet: Haiku 5.5 printed the SRS and OpenAPI as
faithfully as Sonnet 5.5 (9–10 of 10 both, nothing major), but an
architecture with 15 minor slips against Sonnet's one — table rows turned
into prose, a cited token translated, two documents disagreeing on where a
type lives. Each one costs a `doc-review` round, more than the print saves,
and one agent file cannot hold two models. A writer that pastes the
finished file into the typist's prompt has already spent the tokens the row
exists to save.

## Effort

Effort buys thinking where a row decides, not where it types:

- `low` — nothing to decide: `mechanical-worker`, `doc-typist`, `code-explorer`;
- `medium` — transcription and the structural passes: `impl-lite`,
  `plan-review-medium`, `doc-review-low`, `figma-sonnet`; and `design-hard`
  (below);
- `high` — every row that closes decisions: the other implementers, the
  writers, and the remaining reviewers, `review-full-plan` and
  `docs-consistency-checker` included;
- `xhigh` — only the single-shot adversarial judgments where a missed
  finding is the expensive failure: `review-hard`, `plan-review-hard`;
- `max` — not used.

What was measured, and what was not:

| Row | Effort | Evidence |
|---|---|---|
| `review-full-plan` | `high` | 2026-10-01: the planted defect found 12 of 12 times at `medium`, `high`, `xhigh`, `max`, no false blockers; `xhigh` cost 1.6× `medium`, `max` 2.8×, adding only P2 notes |
| `design-hard` | `xhigh`, `opus` | 2026-10-09, a Full-trigger ledger (money, partner API, tenant isolation, 54-ФЗ), two runs per arm, blind: Opus 5.5 `xhigh` against Fable 5.1 `medium`. DB schema — Opus won both pairs clearly, depth 4 against 3 (it puts tenant isolation, refund caps and audit into constraints); architecture — Opus won both clearly, depth 4–5 against 4 (Fable had a lock-order contradiction and a transaction held across a provider call); OpenAPI — one pair each, equal depth. Opus cheaper on the API and architecture ($3.5–4.9 and $14–15 against $6.2 and $17–19), dearer and about twice as slow on the schema ($7–8 against $5–6) |
| `mechanical-worker` | `low`, `haiku` | 2026-10-07: Haiku 5.5 at `low` matched Sonnet 5.5 at `low` byte for byte on a four-unit mechanical plan, two runs each |
| `doc-typist` | `low`, `sonnet` | 2026-10-07: Haiku 5.5 equal on SRS and OpenAPI, 15 minor slips against 1 on an architecture — kept on Sonnet |
| `plan-hard` | `xhigh`, `opus` | 2026-10-09, the same ledger, two runs per arm against Fable 5.1 `high`: equal depth (4) and assertions, Fable won both blind pairs only slightly (it closed decisions the inputs allowed; Opus raised some as blocking questions); review findings noisy both ways. Opus ~25% cheaper ($25–29 against $32–47 a plan with its review); the owner chose one model for every writer |

## What this produces on a typical plan

Code output, `impl-ui`, and every review fix that needs judgment run on
Sonnet; grade-0 units and mechanical fixes on Haiku. Code review runs on Opus: the screen is written once, and review runs
once per reviewed unit (twice when the risk pass fires), and the whole run
once. Design, SRS, and plan writers stay Sonnet and Opus.
If a plan's Opus spend is dominated by transcription-sized diffs that are
not screens, the review roster is firing High passes on Low units.
