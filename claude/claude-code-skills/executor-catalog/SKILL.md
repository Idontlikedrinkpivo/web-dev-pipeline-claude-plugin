---
name: executor-catalog
description: >-
  The single map from a named executor (implementers, reviewers, writers,
  doc-typist, Figma rows) to its agent file, which alone holds the model and
  effort, and to who dispatches it, with nesting and escalation. No OpenAI /
  gpt-* models. Use when a stage routes a unit or dispatches a writer or
  reviewer, when asked which model runs a task, or when adding, retiring or
  re-pointing an executor. Not a workflow: it decides no order and
  implements nothing.
---

# Executor Catalog

Plans name **executors**. This file says **who** each executor is and **when**
it runs: its tier, its branch, and the skill that dispatches it. **How** it
runs lives in one agent file per row, `_agents/<name>.md` in this skills
folder: the model, the effort, the tools, and a short system prompt. The
agent's name is the row's Name. A model rename, a price change, or an effort
change edits one agent file and nothing else; no plan is rewritten, no skill
hardcodes a model.

This file is what a stage needs at dispatch time. Why each row has its model
and effort: `references/model-economics.md`. How to add, retire, or re-point a
row: `references/maintaining.md`. Neither is needed to dispatch.

**A name belongs to its branch.** `impl-*` and `mechanical-worker` write code,
`review-*` judge a diff against a unit spec, `plan-review-*` judge a plan,
`doc-review-*` judge a finished document, `design-*` settle a design document,
`plan-*` settle an implementation plan, `srs-author` settles the SRS,
`doc-typist` prints any of those, `figma-*` draw frames, `screen-writer` writes
screen specs from frames. A name borrowed from
another branch because its tier looks right is a failed dispatch: it runs the
right model on the wrong packet.

## Names: skills and agents carry the plugin prefix

Everything in this set ships as the `dev-pipeline` plugin. In the text of
any skill, a short name — `work`, `plan`, `screen-spec`, `impl-ui` — means
the one from this plugin. Whenever a skill is **invoked** (the `Skill`
tool) or an agent is **dispatched** (the `Agent` tool), use the full name:
`dev-pipeline:work`, `dev-pipeline:impl-ui`. A short name in prose is for
reading; a full name in a call is for routing. If another plugin or a
personal skill has the same short name, the full name is the only way to
be sure this set's version runs.

## The catalog

Every row names its dispatcher; a row nobody dispatches is deleted. Every Name
is also an agent, dispatched as `subagent_type: "<name>"`; its file, not this
table, holds the model and effort.

| Tier | Branch | Name | Dispatched by | Runs |
|---|---|---|---|---|
| **0** | code | `mechanical-worker` | `work` (unit or nested) | renames, moves, config values, regeneration, applying a settled shape to N sites; also the fix-it hand for a mechanical review finding |
| **Low** | code | `impl-lite` | `work` | transcribing a fully specified artifact into working code against an existing local pattern — including README / changelog / doc-comment units |
| **Mid** | code | `impl-medium` | `work` | closing the local decisions a Mid unit leaves open, then proving them |
| **High** | code | `impl-hard` | `work` | designing the missing part inside given boundaries: auth, money, transaction and idempotency shape, cross-cutting contracts |
| **Escalation** | code | `impl-critical` | `work` (escalation only) | the tier above High, for a unit that came back `BLOCKED` or `HARDER_THAN_EXPECTED`; it repeats while each round makes progress (`pipeline` → `references/convergence.md`). Same model as `impl-hard`: a new dispatch with the previous report, not a stronger model. Not a retry of `impl-ui` |
| **UI** | code | `impl-ui` | `work` | frontend that implements a screen spec citing a Figma `nodeId`: the screen and its states, or a component whose shape comes from that frame; or the theme unit that carries the `🎨 Tokens` variables into the theme file after a `ui-design` restyle. Any grade. A retry stays on this row. UI units never run in parallel (`work`). Not a Figma drawing (`figma-sonnet`, `figma-opus`) |
| **Mid** | review | `review-medium` | `code-review-unit` | a Mid unit's diff against its unit spec; also the batched pass over accumulated Low units |
| **High** | review | `review-hard` | `code-review-unit` | adversarial review of a High unit — deliberately not the implementer's alias |
| **Run** | review | `review-full-plan` | `code-review-full` | once per run: cross-unit drift, aggregate invariant/AC coverage, definition of done, over the whole branch diff |
| **Mid** | plan-review | `plan-review-medium` | `plan-review` | the structural half of a plan review: dependency graph, parallel safety, citation integrity, coverage ledger, executor names, plan hygiene |
| **High** | plan-review | `plan-review-hard` | `plan-review` | the judgment half: whether a unit can land green alone, whether its grade survives the cascade, whether a scenario is writable before the code |
| **Low** | docs-review | `doc-review-low` | `doc-review` | coherence and feasibility: the document agrees with itself. Always on |
| **Mid** | docs-review | `doc-review-medium` | `doc-review` | design language and scope, when those signals are present — not whether the premise is right |
| **High** | docs-review | `doc-review-hard` | `doc-review` | premise, security decisions, or falsifying the document |
| **Set** | docs-review | `docs-consistency-checker` | `docs-consistency` | the finished document set read together: traceability both ways and one meaning per name, field, enum, number, status, error, and role. Read-only, one dispatch per check |
| **Write** | requirements | `srs-author` | `srs-writer` | settles the SRS, including a grill-reversal pass. No grade cascade. The session asks and grills. `doc-typist` prints the file |
| **Low** | design | `design-lite` | `clean-architecture-design` (every mode: foundation, domain model, scenarios of an area), `db-schema-design`, `openapi-spec-generator` | judgment for a bounded one-table / few-operation / plain-CRUD document. `doc-typist` prints it |
| **Mid** | design | `design-medium` | same three | close local design decisions for a Modest / one-slice document. `doc-typist` prints it |
| **High** | design | `design-hard` | same three | Full-trigger, security-heavy, or cross-section design judgment. `doc-typist` prints it |
| **Low** | plan-writer | `plan-lite` | `plan` | slice a fully bounded increment along seams the design already drew. `doc-typist` prints the plan |
| **Mid** | plan-writer | `plan-medium` | `plan` | close the remaining slice and grade decisions. `doc-typist` prints the plan |
| **High** | plan-writer | `plan-hard` | `plan` | Full-trigger, security, or cross-section slicing. `doc-typist` prints the plan |
| **Print** | docs | `doc-typist` | nested by `srs-author`, the three `design-*` rows, and the three `plan-*` rows | prints a document those rows already settled, including sibling D2 and `open-questions.md` rows the settlement named. No new decision |
| **Read-only** | any | `code-explorer` | `plan` (brownfield inventory), `grill-me` (facts), `brainstorm` (scout and claim verifier) | locating patterns, files, and call sites in a repo whose code *is* the design; never edits |
| **Edit** | figma | `figma-sonnet` | `ui-design` | elements added or changed on frames that already exist, or those frames restyled to a chosen visual direction. Not a new screen and not a redesign |
| **Build** | figma | `figma-opus` | `ui-design` | frames from an empty file, a new screen, or a redesign of an existing screen, from the SRS; the style tiles of a visual direction |
| **Write** | screen | `screen-writer` | `screen-spec` | one front-end spec per screen from the frames and the OpenAPI contract; writes the file itself; decides no behaviour the frames did not |
| **Write** | ui-test | `ui-test-writer` | `ui-test-cases` (mode write) | user test cases from SRS acceptance criteria and screen specs; decides no behaviour |
| **Run** | ui-test | `ui-test-runner` | `ui-test-cases` (mode run) | Playwright tests from the cases, run against the app started locally, screens compared with frames; never edits app code |

`plan` writes only names from `references/assignable-implementers.md`;
`plan-review` checks that list, not this table.

## Dispatch contract

Every skill in a `Dispatched by` cell calls its row with Claude Code's `Agent`
tool like this. Consumers point here instead of restating it.

- **The row picks itself.** The grade, the cascade, or the routing table below
  names the row; dispatch it. Do not ask the user which row or model to use.
  Instead, the stage's closing report names every row it dispatched, with the
  grade when a cascade picked it (`Mid · plan-medium`), so the user sees who
  did the work.
- **`subagent_type` is `dev-pipeline:<Name>`, and the call passes no
  `model`.** The plugin namespace keeps the row unambiguous when another
  plugin or a personal agent has the same short name (`impl-ui`,
  `review-hard`). The bare name is only the fallback for a setup without
  the plugin (`install.sh`) or a test harness that passes agents directly —
  use it only when the `Agent` tool lists no `dev-pipeline:` form. A `model` on the call overrides the agent file, so the
  tier would silently run whatever was typed instead of what its file says.
  Never `general-purpose`, `Explore`, or another built-in agent: those carry
  none of the row's model, effort, tools, or prompt.
- **Before every `Agent` call, write the resolved row in this turn:**
  `Name | subagent_type`, prefixed with the grade when a cascade picked the row
  (`Mid | design-medium | dev-pipeline:design-medium`). You may append the
  model and effort read from the agent file (`· opus · high`); copy them from
  the file, never from memory.
- **A model the user names.** Only when the user, on their own, names a model
  for this dispatch — a Claude alias (`haiku`, `sonnet`, `opus`, `fable`) or a
  full Claude model id — dispatch the same row and pass that value as `model`
  on this call only; the file's effort, tools, and prompt still apply. The line
  says so: `design-medium | design-medium | model override: sonnet (user; file:
  opus)`. Never a `gpt-*` model, `inherit`, or the session model, and never the
  implementer's alias on a review row — refuse those with the reason. The
  override is this dispatch only; an escalation goes back to the file.
- **A rejected `subagent_type`:** retry once with the bare name. If both are
  rejected, the agent is not installed.
  **Stop** and tell the user to install the `dev-pipeline` plugin (or run
  `bash install.sh` in the skills folder that holds `_agents/`) and restart
  the session. Do not fall back to `general-purpose` with a hand-typed model,
  and do not do the row's work on the session model.
- **Parallel dispatches** (a `work` wave) each pass `isolation: "worktree"` so
  workers never share a working directory. Before integrating (`work` Step
  5.1), merge or cherry-pick each worker's worktree branch into the main tree;
  if that is not possible, run the wave serially.

```
Mid | impl-medium | dev-pipeline:impl-medium
Agent(subagent_type: "dev-pipeline:impl-medium", prompt: <worker packet for U4>)
```

Wrong: `Agent(subagent_type: "general-purpose", model: "sonnet")` — the row's
effort, tools, and prompt are gone and the model was typed from memory. Also
wrong: `Agent(subagent_type: "impl-medium", model: "sonnet")` when the user
named no model — the `model` overrides the file.

**Slug hygiene.** A model alias is written in exactly one place: the `model:`
line of the row's agent file. No plan, packet, skill, or dispatch line carries
one — a model in a plan is a `plan-review` finding. If the harness rejects the
alias in an agent file, that is a **stop**: do not edit the file to a
neighbour, do not pass a different `model` on the call, and do not fall back
to the session model or `general-purpose`. Report the file, the rejected
alias, and the tier, and let the user re-point that file. A rejected alias is
never replaced by a `gpt-*` one.

**Scope.** This catalog routes pipeline dispatch only. Work outside the
dispatching skills — an ad-hoc edit, a question, a debugging detour — runs on
the session model, unrouted: grading is a planning-time decision recorded in a
plan or a design grade. Ad-hoc work heavy enough to want routing is heavy
enough to be a plan.

## Nesting

A dispatched row may hand work to one nested target; nested targets dispatch
nothing further (session → row → nested target). A nested call follows the
Dispatch contract like any other, with no `model`.

- **`mechanical-worker`** — a code unit's implementer may hand out the typing
  named in the plan's `Nested does` and keep the decision. `plan` may name only
  this nested target. It pays off when the mechanical part is settled and
  repetitive; two files is not worth the dispatch.
- **`doc-typist`** — `srs-author`, the three `design-*` rows, and the three
  `plan-*` rows hand the printing here after the document's decisions are
  settled. Packet: `references/doc-typist-prompt.md`. The session does not
  dispatch it and does not ask about it. A plan file never names it.

| Rule | Why |
|---|---|
| Only those two are nested targets | anything else has judgment that does not delegate cleanly |
| Nesting never raises capability | a harder document gets a higher writer, not a smarter typist; a harder unit gets a higher `Implementer` |
| The parent owns the output | it reads the file and may re-dispatch the typist once. It does not type the correction |
| The parent does not paste the finished document | that spends the output tokens the nest exists to save. The prompt carries a settlement — one line per decision — plus paths to read |
| Deciding what a test asserts never nests | `mechanical-worker` may only replicate an assertion the implementer already wrote across N settled cases |

**A two-phase unit is one executor, twice.** Both phases of a `work` two-phase
dispatch go to the unit's named implementer and count as one attempt of that
unit (`work/references/two-phase-dispatch.md`).

## Escalation

A unit returning `BLOCKED` or `HARDER_THAN_EXPECTED` moves up one tier per
failure: grade 0 → Low → Mid → High → `impl-critical`.

- Re-dispatch carries the previous attempt's report — what was tried, what
  failed, what it observed. A blind retry buys nothing.
- At `impl-critical` the unit repeats, with every previous report, while
  each round makes progress; when progress stops it is a **stop** — the
  unit is under-specified or the design is wrong, and both belong to the
  user (`pipeline` → `references/convergence.md`).
- `impl-critical` is terminal. On the code branch the higher tier stays on the
  same alias (its agent file may raise the effort); the retry's value is the
  previous report in a fresh dispatch.
- `impl-ui` is not on that ladder: a difficulty return re-dispatches `impl-ui`
  once with the report.
- Where an escalation is recorded: `work` Step 6. If the same *kind* of unit
  escalates repeatedly across runs, fix the cascade in
  `plan/references/complexity.md`, not the individual grades.

## Routing

Each dispatching skill owns *what* its executor does; these tables own only
*who* runs it. Do not do a row's work on the session model to "save a
dispatch", and do not replace a failed dispatch with the session.

### Review routing

| Unit grade | Review (`code-review-unit`) |
|---|---|
| 0 | none — the orchestrator's diff inspection is the review |
| Low | none per unit; one `review-medium` pass over the batch |
| Mid | `review-medium` on the unit diff |
| High | `review-hard` on the unit diff, plus a second risk pass |

The whole-run review is one `review-full-plan` dispatch per run
(`code-review-full`), never doubled and never re-dispatched with a `model`.

### Plan-review routing

| Half | Executor | Lenses |
|---|---|---|
| Structural | `plan-review-medium` | dependency graph, parallel safety, citation integrity, coverage ledger, executor validity, existing work, plan hygiene |
| Judgment | `plan-review-hard` | commit atomicity, grade calibration, test-first writability |

Never point the judgment half at `plan-review-medium`: arguing with a grade is
the same work that produced it.

### Document-review routing

| Persona | Executor |
|---|---|
| `coherence-reviewer`, `feasibility-reviewer` | `doc-review-low` |
| `design-lens-reviewer`, `scope-guardian-reviewer` | `doc-review-medium` |
| `product-lens-reviewer`, `security-lens-reviewer`, `adversarial-document-reviewer` | `doc-review-hard` |

`doc-review` decides which personas fire. Do not point a hard persona at a
lower row to save a dispatch.

The whole-set check is not a persona: `docs-consistency` dispatches
`docs-consistency-checker` once, and never a `doc-review-*` row in its
place.

### SRS-writer routing

Every SRS goes to `srs-author`; no grade. Grill reversals are a second
dispatch of the same row, which nests `doc-typist` to edit the file. Packet:
`references/srs-writer-prompt.md`.

### Design-writer routing

| Grade (`references/design-complexity.md`) | Executor |
|---|---|
| Low | `design-lite` |
| Mid | `design-medium` |
| High | `design-hard` |

The writer settles the document and its D2 files and nests `doc-typist` to
print them. Packet: `references/design-writer-prompt.md`.

### Plan-writer routing

| Grade (`references/plan-complexity.md`, not the unit cascade) | Executor |
|---|---|
| Low | `plan-lite` |
| Mid | `plan-medium` |
| High | `plan-hard` |

The writer settles the units and nests `doc-typist` to print the file.
Packet: `references/plan-writer-prompt.md`.

A revise after `plan-review` is graded separately, by its blocking
findings, not by the plan: `references/plan-complexity.md` → Grading a
revise. A plan graded High whose review asks only for spelled-out text
fixes is revised by `plan-lite`.

### Figma routing

| Situation (`ui-design` decides) | Executor |
|---|---|
| Empty file, a new screen, a redesign, or the whole interface redrawn on a new page | `figma-opus` |
| Style tiles for choosing the visual direction (`MODE direction`) | `figma-opus` |
| Elements only, on frames that already exist | `figma-sonnet` |
| The existing frames take a chosen visual direction; structure, texts and ids stay (`MODE restyle`) | `figma-sonnet` |
| Renaming a designer's layers by action and adding annotation frames (`MODE rename`, nothing visible changes) | `figma-sonnet` |

### Screen-spec routing

Every screen spec goes to `screen-writer`; no grade. Packet:
`screen-spec/references/writer-prompt.md`.

Packet: `references/figma-packet.md`.

## References

- `references/assignable-implementers.md` — the only names `plan` may write.
- `references/worker-prompt.md` — the packet a code executor receives and the
  report it returns (used by `work`).
- `references/design-complexity.md`, `references/plan-complexity.md` — the
  cascades that grade a design document and a plan.
- `references/srs-writer-prompt.md`, `references/design-writer-prompt.md`,
  `references/plan-writer-prompt.md`, `references/doc-typist-prompt.md`,
  `references/figma-packet.md` — the writer and Figma packets.
- `references/model-economics.md` — why each row has its model and effort, and
  what was measured. Read before re-pointing a tier.
- `references/maintaining.md` — adding, retiring, or re-pointing a row.
- `_agents/<name>.md` — one agent per row: model, effort, tools, short prompt.
  `_agents/README.md`, `install.sh`, `.claude-plugin/plugin.json` — the two
  ways to install them.
- `doc-review` (skill) — the personas and their packets.
