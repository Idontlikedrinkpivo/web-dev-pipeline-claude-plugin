---
name: brainstorm
description: >-
  Turns a vague or ambitious software idea into a business-requirements
  document (Goal Capsule and Product Contract) under
  documentation/requirements/. Use when the user wants to brainstorm, think
  through scope, decide what to build, frame a product before an SRS, or
  asks for a blindspot pass — «давай подумаем», «что строим». Not for
  implementing specified work, debugging, code review, or judging an
  external library; a request for code now goes to `srs-writer` first.
---

# Brainstorm a Feature or Improvement

Brainstorming helps answer **WHAT** to build through collaborative dialogue. The durable output is a **business requirements document** — a lightweight PRD / feature brief with clear functional and non-functional requirements, use cases, and acceptance criteria, so later technical work does not need to invent product behavior, scope boundaries, or success criteria.

This skill explores, clarifies, and documents decisions; it does not implement code. Its document is consumed by `srs-writer` — name that skill. Architecture, API/DB design, and implementation come after the SRS, not instead of it: do not skip to architecture, code, or "technical planning" as if the SRS stage did not exist.

**Implementation request.** If the user asks to write code, a service, controllers, or tests **now**, refuse. Do not start those skills. The next named writer is still `srs-writer`.

## Setup

Once, at the start of this invocation and before any subagent dispatch, read `references/setup.md` and run its context fence exactly as written there — it prints directives this run follows.

## Core Principles

1. **Assess scope first** - Match the amount of ceremony to the size and ambiguity of the work.
2. **Be a thinking partner** - Suggest alternatives, challenge assumptions, and explore what-ifs instead of only extracting requirements.
3. **Resolve product decisions here** - User-facing behavior, scope boundaries, and success criteria belong in this workflow. Detailed implementation belongs in planning.
4. **Keep implementation out of the Product Contract by default** - Do not include libraries, schemas, endpoints, file layouts, or code-level design unless the brainstorm itself is inherently about a technical or architectural change.
5. **Right-size the artifact** - Simple work gets a compact business requirements document or brief alignment. Larger work gets a fuller Product Contract. Do not add ceremony that does not help planning.
6. **Apply YAGNI to carrying cost, not coding effort** - Prefer the simplest approach that delivers meaningful value. Avoid speculative complexity and hypothetical future-proofing, but low-cost polish or delight is worth including when its ongoing cost is small and easy to maintain.
7. **Do not turn coverage into decomposition** - For software brainstorms, treat named devices, providers, and data sources as coverage requirements, not automatically as separate integration workstreams. Split them only when a shared access path cannot satisfy a named requirement. Leave connector selection to planning unless that choice materially changes product scope or behavior.
8. **Keep one coherent work unit per artifact** - When a request contains independently valuable outcomes that can be planned and delivered separately, choose one as the current focus before deep exploration. Preserve how the surrounding work is currently understood without turning tentative future areas into requirements for this plan.

## Interaction Rules

These rules apply to every brainstorm.

1. **Ask one question at a time** - One question per turn, even when sub-questions feel related. Stacking several questions in a single message produces diluted answers; pick the single most useful one and ask it.
2. **Prefer single-select multiple choice** - Use single-select when choosing one direction, one priority, or one next step.
3. **Use multi-select rarely and intentionally** - Use it only for compatible sets such as goals, constraints, non-goals, or success criteria that can all coexist. If prioritization matters, follow up by asking which selected item is primary.
4. **The question is one chat message** — Follow `grill-me` → "How a question is shown". One question: what is being decided, what each option changes, the real terms with what they mean here, and which option you recommend. Then stop. The user answers by sending a message. Do not call `AskUserQuestion` or any other question card. This holds for opening and elicitation questions too, not only narrowing. Never silently skip the question. On a visual topic, the Phase 1.3 visual-probe gate comes before this rule.
5. **Use an open-ended question only when the question is genuinely open** - Ask it in the chat with no options when the answer is inherently narrative, when presented options would steer a diagnostic or introspective answer, or when you cannot write 3-4 genuinely distinct, plausibly-correct options without padding. The test: if you'd be straining to fill the option slots, the question is open — ask it open-ended. Rule 1 still applies: one question per turn.
6. **Open-ended questions earn their place only when they're specific enough to elicit a substantive answer** - Apply Rule 5 silently: just ask the question, never narrate the form choice. The question must give the user something concrete to anchor on. Good: *"What's the most concrete thing someone's already done about this — paid for it, built a workaround, quit a tool over it?"* — it names what counts as an answer. Too thin: *"What's your take?"* — nothing to bite into, and framings that imply a short answer ("briefly", yes/no) waste the open question the same way.

## Artifact Root

This skill writes one living business requirements document per project, at a
fixed path:
`<repo-root>/documentation/requirements/business-requirements/business-requirements.md`.
The path carries no date and no topic name — the repo already names the project.
Resolve `<repo-root>`
when you first compose a path (run `git rev-parse --show-toplevel`; if that
fails — not a git repo — use the current working directory as `<repo-root>`).
Create that folder if it does not exist yet. There is no config override and
no `docs_root` lookup. Unresolved items go in `open-questions.md` in that same
folder, not in a section of the document.

**The document is unversioned** — a working draft, not a contract; versioning
starts at `srs-writer`. On every write, greenfield or increment: no `version`
in the frontmatter and no `## Changelog` table; if a leftover `version` or
changelog is already in the file, delete them on this write.

**A feature added to a product that already has a business requirements document
is an increment.** Read the `doc-versioning` skill: keep the existing path,
edit in place, extend the R namespace with unused numbers, set `updated:`
to today. Do not write a second business requirements document for the same
product — the resume path below is the mechanism.

## Output Guidance

- **Prioritize decision-relevant detail** - Preserve the facts, tradeoffs, and caveats needed for the next decision; trim introductions, repetition, and optional background first.

## Feature Description

The **feature description** is the input this skill was invoked with — what to explore, present in the current prompt or conversation, whether the user provided it directly or a calling skill passed it.

**If no feature description was provided, ask the user:** "What would you like to explore? Please describe the feature, problem, or improvement you're thinking about."

Do not proceed until you have a feature description from the user.

**Session-settled decisions.** The invoking conversation, or a distilled brief passed as invocation input — from the user or a calling skill — may carry decisions already examined-and-chosen. Read `references/settled-decisions.md` before classifying conversation-carried decisions — it carries the settlement test, the two provenance classes, the annotation shape, and capture rules. Skipping the classification fails in both directions: re-asking a decision the user already made, or promoting an unexamined assertion to settled.

## Execution Flow

### Phase 0: Resume, Assess, and Route

#### 0.1 Resume Existing Work When Appropriate

This resume scan needs `documentation/requirements/`, so it applies only to a repo-backed run. If there is no git repository, skip the scan and continue.

In a repo-backed run, if the user references an existing brainstorm topic or document, or `documentation/requirements/business-requirements/business-requirements.md` already exists:
- Read the document
- Confirm with the user before resuming: "Found an existing requirements-only document for [topic]. Should I continue from this, or start fresh?"
- If resuming, summarize the current state briefly, continue from its existing decisions and outstanding questions, and update the existing document instead of creating a duplicate

#### 0.1b Classify Task Domain

Before proceeding to Phase 0.2, classify whether this is a software task. The key question is: **does the task involve building, modifying, or architecting software?** -- not whether the task *mentions* software topics.

**Software** (continue to Phase 0.2) -- the task references code, repositories, APIs, databases, or asks to build/modify/debug/deploy software.

**Not software** -- the idea is about something other than building software. This skill writes software requirements only: say so in one line and help directly in the chat, without phases or a document.

**Neither** (respond directly, skip all brainstorming phases) -- the input is a quick-help request, error message, factual question, or single-step task that doesn't need a brainstorm.

#### 0.2 Assess Whether Brainstorming Is Needed

Requirements are already clear when the opening gives specific acceptance criteria, points to existing patterns to follow, describes the exact expected behavior, and has a constrained, well-defined scope.

When they are clear:

1. Confirm your understanding briefly and offer concise next-step options instead of a long brainstorm.
2. Skip Phases 1.1 and 1.2.
3. Still classify the tier in Phase 0.3 — the tier, not the clarity, decides the Phase 2.5 path, so a clear Standard or Deep opener still gets the full confirmation.
4. Go to Phase 1.3 if something is still open, otherwise straight to Phase 2.5.
5. Write a short business requirements document only when a durable handoff to planning or later review is worth having (Phase 3 decides).

#### 0.3 Assess Scope

1. **Classify the tier** from the feature description plus a light repo scan:
   - **Lightweight** — small, well-bounded, low ambiguity
   - **Standard** — normal feature or bounded refactor with some decisions to make
   - **Deep** — cross-cutting, strategic, or highly ambiguous

   If the tier is unclear, ask one targeted question, then proceed.
2. **Run the coherent-work gate.** Look for more than one independently plannable product outcome: each has its own user value or acceptance boundary and could ship without the others. Shared actors, one end-to-end outcome, or coverage across named devices/providers do not by themselves justify a split. Keep the work together when the outcomes cannot be independently useful or validated, or when separating them would force this Product Contract to invent the missing shared behavior. When the gate finds several areas:
   1. Propose a plain-language breakdown. State only relationships supported now: which areas depend on or enable others, share a product rule, or can proceed independently.
   2. Ask which one area this brainstorm owns. If the user already chose one, carry it forward instead of asking again.
   3. Make that area the sole source of Requirements, Flows, and Acceptance Examples. Other areas stay contextual candidates, not scope.
   4. Keep the broader picture for Phase 3's **How This Work Fits Together** section. Mark tentative relationships as tentative; later brainstorms may revise, split, merge, or discard them.
   5. Name the current area in the Goal Capsule objective and say the surrounding areas are not active scope.

   The gate narrows the active artifact. It does not create a parent plan or a roadmap.
3. **For Deep, pick the sub-mode** — whether the brainstorm inherits product shape or must establish it:
   - **Deep — feature** (default): primary actors, core outcome, positioning, and primary flows are already established in the product or repo. The brainstorm extends or refines within that shape, with the current Deep behavior unchanged.
   - **Deep — product**: any of those is materially unresolved, including positioning against adjacent products. Existing code lowers the odds but does not rule it out — a half-built tool with ambiguous shape is still product-tier. Product tier adds Phase 1.2 questions and Product Contract sections.
4. **Check the two tripwires.** Each one only loads a reference now; the reference decides when its offer fires, so do not fire anything here.
   - **Visual** — the feature is inherently visual or spatial: drawing/canvas tools, annotation behavior, visual editors, UI layout or navigation, interaction states, charts, diagrams, animation, maps, timelines, spatial flows (strong signals: freehand vs constrained drawing, layout comparisons, state/flow placement). Read `references/visual-probes.md`.
   - **Unfamiliarity** — the user says they lack working knowledge of the territory ("I know nothing about X", "never touched the auth modules", "I don't know what I should be asking"). Read `references/blindspot-pass.md`.

#### 0.4 Surface the Workflow Spine

1. Skip this step for Lightweight.
2. For Standard and Deep, look for the task-tracking tool (`TaskCreate`). If tools load on demand, search for it with `ToolSearch` before concluding there is none.
3. Found one: read `references/task-spine.md` and create the five-task spine it defines — here, not earlier, because the tier is unknown until 0.3.
4. Found none: continue without simulating a task list in chat — a list the user cannot tick off is noise.

The list is a view for the user; it never changes what a phase requires.

### Phase 1: Understand the Idea

#### 1.1 Existing Context Scan

Scan the repo before substantive brainstorming. **Lightweight:** search for the topic, check whether something similar already exists, and move on.

**Standard and Deep:**

1. **Constraint check (inline).** Use the project's active instructions and conventions already in your context. Read `STRATEGY.md` if it exists (product direction) and `CONCEPTS.md` if it exists (canonical vocabulary). Use canonical names in dialogue, approaches, and the Product Contract. A source that adds nothing is skipped.
2. **Create the scratch directory** with this block, substituting a short unique run slug, and keep the printed absolute path:

```bash
SCRATCH_ROOT="/tmp/brainstorm-$(id -u)";
if [ -L "$SCRATCH_ROOT" ]; then echo "unsafe scratch root symlink: $SCRATCH_ROOT" >&2; exit 1; fi;
(umask 077; mkdir -p "$SCRATCH_ROOT") || exit 1;
if [ -L "$SCRATCH_ROOT" ] || [ ! -O "$SCRATCH_ROOT" ]; then echo "scratch root is not owned by the current user: $SCRATCH_ROOT" >&2; exit 1; fi;
chmod 700 "$SCRATCH_ROOT" || exit 1;
SCRATCH_DIR="$SCRATCH_ROOT/brainstorm/<run-id>";
(umask 077; mkdir -p "$SCRATCH_DIR") || exit 1; chmod 700 "$SCRATCH_DIR" || exit 1;
echo "$SCRATCH_DIR";
```

3. **Dispatch the grounding scout:** `code-explorer` through `executor-catalog` (`subagent_type: "code-explorer"`, no `model` — the agent file holds it). Not `Explore` or `general-purpose`: an uninstalled agent is named to the user with `install.sh`, per the catalog's Dispatch contract. Without a subagent primitive, do the same work inline or serially. With background dispatch, go on to Phase 1.2/1.3 **without waiting** — the scout runs during the user's think-time on the opening questions. Scout prompt:

   > Gather grounding for a requirements brainstorm about **{topic}** in this repo. Search first with the native file-search and content-search tools, then read targeted sections — budget ~20 reads, preferring ranges over whole files. Find: whether something similar already exists, the most relevant existing artifacts (brainstorms, plans, specs, feature docs), adjacent examples of similar behavior, and the current state of anything the topic would touch (tables, routes, config, dependencies). Write a **grounding dossier** to `{scratch-dir}/grounding.md`: at most 150 lines of verbatim quotes and short code snippets, each with a `file:line` pointer. Extraction only — quote what the repo says; do not interpret or propose. If the topic has little footprint, write less rather than padding. Return only a gist: 3-5 lines summarizing what the dossier holds, plus its absolute path.

4. **Carry only the gist in the dialogue.** Read the dossier on demand — when the user challenges a claim or an approach needs grounding. It is a verified quote-sheet, always cheaper than re-scanning raw files. If Phase 2 needs it and the scout has not returned, wait for it then.
5. If the scan and scout surface nothing relevant, say so and continue.

Two rules govern technical depth during the scan, for every tier and topic:

- **Verify before claiming.** When the brainstorm touches checkable infrastructure (database tables, routes, config files, dependencies, model definitions), read the source to confirm what exists. A claim that something is absent — a missing table, an endpoint that does not exist, a dependency not in the project's dependency manifest, an unsupported config option — must be verified against the codebase; otherwise label it an unverified assumption.
- **Defer design decisions to planning.** Schemas, migration strategies, endpoint structure, or deployment topology belong in planning — unless the brainstorm is itself about a technical or architectural decision, in which case they are its subject.

#### 1.2 Product Pressure Test

Before generating approaches, find the rigor gaps in the user's opening. This is your own analysis, not a checklist shown to the user.

1. Read `references/product-pressure-test.md` and take the lenses for the Phase 0.3 tier (Lightweight / Standard / Deep / Deep-product).
2. Read the opening against them and list only the gaps that actually exist. A fuzzy opening may earn three or four; a concrete, well-framed one may earn zero.
3. Do not count a session-settled decision as a gap — it is already probed. Spend the scrutiny on unexamined assertions instead, so each gets its one examination here rather than being re-litigated downstream.
4. Carry the list into Phase 1.3, which fires each gap as a probe.

#### 1.3 Collaborative Dialogue

Follow the Interaction Rules above: one chat question per Rule 4. **Before each question, check two gates:**

- **Blindspot gate — before the first substantive question into flagged territory.** If the Phase 0.3 unfamiliarity tripwire fired, fire the blindspot offer from `references/blindspot-pass.md` first. Questions about the user's own problem, users, and evidence proceed normally — the gate is territory-scoped. It also arms mid-dialogue without a tripwire: when two consecutive answers show the user *cannot evaluate* the question's substance — not merely has not decided — read the reference and offer the pass then. The offer is one chat question per Rule 4; never silently switch into teaching.
- **Visual-probe gate — before the first shape decision.** If the Phase 0.3 visual tripwire fired, then before raising any decision about shape, behavior, state, layout, flow, or a diagram, fire the text-vs-visual offer from `references/visual-probes.md`. Check it against the decision you are about to raise (offer unless this decision has already been through the gate), not against a "pending gate" remembered since 0.3. It takes precedence over Interaction Rule 4: do not raise the shape decision until the user has declined visual. **An ASCII preview or text mockup inside the choices does not satisfy the offer** — that is the shortcut this gate exists to stop. The offer is one chat question; the reference owns its wording, the cheapest-probe build, helper invocation, and the display-only feedback contract.

**Then work the dialogue:**

1. Ask what the user is already thinking before offering your own ideas — it surfaces hidden context and prevents fixation on AI-generated framings.
2. Start broad (problem, users, value), then narrow (constraints, exclusions, edge cases).
3. Fire each Phase 1.2 gap as its own direct, **open-ended** probe — one probe per gap. A menu would signal which kinds of evidence count and let the user pick instead of producing; an open probe forces real observation or surfaces real uncertainty. The reference's "when present, ask…" line is the probe; phrase it per Interaction Rule 6. Spread the probes across the conversation, interleaved with narrowing moves, and probe every gap before Phase 2. Do not fire them back to back at the start: a pre-flight gauntlet of five hard questions reads as an exam, and the answers get shorter and vaguer with each one.
4. When the attachment gap is present (judged from the opening), make it the last probe before Phase 2 — even if narrowing already produced a shape, because its job is to pressure-test the framing Phase 2 would otherwise inherit.
5. When a probe's answer shows genuine uncertainty, record it as an explicit assumption in the Product Contract instead of dropping the probe.
6. Throughout: clarify the problem frame, validate assumptions, ask about success criteria, and make requirements concrete enough that planning will not invent behavior. Surface dependencies only when they materially affect scope. Resolve product decisions here; leave technical choices to planning. Bring ideas, alternatives, and challenges instead of only interviewing.
7. **Integration check, before exiting.** Combine what the user has said and look for non-obvious consequences one-question-at-a-time dialogue hides: user-stated X plus user-stated Y plus your default Z ("if mute lives on the rule AND we don't warn on delete, then rule-delete silently loses pause state"). Probe each genuine combination effect now, open-ended, one probe each. Phase 2.5's call-outs are a safety net for residuals (silent agent inferences, pre-loaded contexts with no dialogue), not a punt list for consequences you could ask about now.

**Exit Phase 1.3** when all of these hold, or the user explicitly wants to proceed:

- the primary actor/user is identified or marked unknown;
- the desired outcome is stated;
- the in-scope and out-of-scope boundaries that matter are known;
- success criteria or acceptance signals are known or recorded as assumptions;
- every Phase 1.2 gap has been probed or recorded as an assumption;
- no integration-check question is pending.

A session-settled decision counts as already-probed toward every clause — never re-ask it.

**Example — one Standard-tier turn.** The opening was "поддержку будят ночные уведомления, надо дать их глушить"; the counterfactual gap was already probed (open question, no card: «Что поддержка делает сегодня, когда пинг приходит в 3 ночи — выключает телефон, отписывается от канала, терпит?» → «выключают звук у всего Slack»). The next turn narrows:

```text
Вопрос 1. Что глушим: одного человека или один канал?

Сейчас пинги в 3 ночи приходят из канала #support-alerts.
- A. Человека. Каждый сотрудник сам выключает себе всё на ночь;
  дежурный тоже может выключить и пропустить аварию.
- B. Канал. Пауза ставится на правило уведомлений канала и действует
  на всю команду; остальные каналы звучат как раньше.

Рекомендую B: будят не одного человека, а всю поддержку, и решать
это настройкой каждого по отдельности — значит пропустить дежурного.
```

The user answers with a message. That answer becomes "Per-channel over per-user" in the example summary of `references/synthesis-summary.md`. Do not open a question card.

### Phase 2: Explore Approaches

1. **Decide whether there is a choice.** If one approach is clearly best and alternatives are not meaningful, state the recommendation directly, with why, and go to step 7. Otherwise prepare **2-3 concrete approaches** from the research and conversation.
2. **Make them different.**
   - Use at least one non-obvious angle — inversion (what if we did the opposite?), constraint removal (what if X weren't a limitation?), or an analogy from another domain. The first approaches that come to mind usually vary along the same axis.
   - Apply the anti-genericness test: an approach that would appear in a generic listicle for this problem category gets sharpened against the grounding dossier or dropped.
   - At product tier, approaches differ on *what* is built (product shape, actor set, positioning), not *how*. Implementation variants belong at feature tier.
   - When useful, add one higher-upside challenger: the adjacent addition or reframing that most increases usefulness, compounding value, or durability without disproportionate carrying cost. Present it beside the baseline, not as the default. Omit it when the work is already over-scoped or the baseline is clearly right.
3. **Keep the granularity at mechanism / product shape, not architecture.** Name mechanism-level distinctions ("pause as a rule property" vs "pause as an event filter" vs "pause as a separate entity") and product-relevant trade-offs (plan-tier coupling, complexity surface, migration difficulty). Do not name column or table names, file paths, service classes, JSON shapes, or method names — those belong to later technical planning, and bringing them forward forces architectural decisions on this phase's intentionally shallow research.
4. **For each approach, give:** a 2-3 sentence description, pros and cons, key risks or unknowns, and when it is best suited.
5. **Visual differences.** If the approaches differ spatially, behaviorally, or visually enough that prose would be slower or lower-fidelity, go through `references/visual-probes.md` before presenting them. If the Phase 0.3 tripwire fired and no shape decision has been through the gate yet, the offer fires here. The visual path is opt-in and display-only; text remains a first-class path.
6. **Present all approaches first, then recommend** and say why — a recommendation before the user has seen the alternatives anchors the conversation. Prefer simpler solutions when added complexity has real carrying cost, but do not reject low-cost, high-value polish just because it is not strictly necessary.
7. When relevant, say whether the choice reuses an existing pattern, extends an existing capability, or builds something net new.

### Phase 2.5: Synthesis Summary

The scoping synthesis is the user's last chance to correct scope before the document lands — shaped like what two product collaborators confirm before writing a PRD, not a comprehensive audit and not a one-line preview.

1. **Read `references/synthesis-summary.md` before composing anything.** It owns the two-stage shape, the section keep tests, the bullet budget, the anti-patterns, soft-cut, and routing into the document body; none of that is in this file. Composing from memory reliably produces the known failures: the internal three-bucket draft pasted into chat, implementation detail leaking into the synthesis, the proposal pitch.
2. **Let the reference pick Path A or Path B.** Path A (announce, no confirmation) is **only** Lightweight with no blocking question fired; every other case, including a richly pre-loaded Standard/Deep opener that needed no dialogue, is Path B with an unconditional confirmation. Do not decide the path from memory.
3. **Compose and present** per the reference. Session-settled decisions — common in rich-context Path B openers — render as `Carrying forward:` lines, never as questions or call-outs.

This phase runs for every tier, including Lightweight.

#### 2.6 Claim Verification (inside the Path B confirmation wait)

A fresh-context verifier replaces self-grading: the author confirming its own claims is anchored, and the verifier never saw the dialogue.

1. **Skip** when Path A fired, or when the document will make no checkable claims.
2. **List the checkable claims** the Product Contract will assert, one line each: absence claims ("no retry logic exists"), references to specific files, config, or dependencies, anything planning would build on.
3. **Dispatch `code-explorer`** through `executor-catalog` at the same moment the Path B confirmation question goes up, so it runs during the user's think-time. Same dispatch as the scout (`subagent_type: "code-explorer"`, no `model`). Pass the claim list, the grounding dossier path if one exists (the path, not its contents), and this instruction: verify each claim directly against the codebase — budget ~15 targeted reads — and return a per-claim verdict: **confirmed** (with `file:line`), **refuted** (with the contradicting evidence), or **unverifiable**.
4. Do not block the confirmation question on the verifier.
5. **At Phase 3,** correct refuted claims before writing and label unverifiable ones as explicit assumptions.
6. If the dispatch fails, verify the claims inline before the Phase 3 write — Phase 1.1's verify-before-claiming rule holds either way.

### Phase 3: Capture the Business Requirements Document

Write or update a business requirements document only when the conversation produced durable decisions worth preserving — see `references/brainstorm-sections.md` "Decide whether a doc is warranted at all" for the criteria and the bug-fix stress test. Skip document creation when the user only needs brief alignment and the decisions can flow downstream (a commit message) without a brainstorm artifact in the middle.

When a doc is warranted, compose it using:

- `references/brainstorm-sections.md` — section contract (business requirements document contract, Product Contract hard floor, include-when-material catalog, agency rules, ID conventions).
- `references/markdown-rendering.md` — read it **now**, before composing: it defines how the sections are presented, and composing without it produces drift the section contract alone cannot prevent.

Session-settled decisions land in the Product Contract's Key Decisions section carrying their `session-settled:` annotation (shape in `references/settled-decisions.md`), so any later technical planning can inherit the label into its own decision entries.

**Language.** Write the document in Russian. Do not translate cited tokens.
Required section names and frontmatter keys stay as this skill specifies.

**Write tight.** A section being material is not license to pad it. Hold every kept section to the prose-economy discipline in `references/brainstorm-sections.md`: lead with the decision or outcome, one idea per sentence, a requirement is intent plus at most one qualifier, defer forks to `open-questions.md` beside the file rather than specifying both arms, resolve superseded text in place rather than stacking strata.

Write to `documentation/requirements/business-requirements/business-requirements.md` (folder, increment, and the no-`version` / no-changelog rule are in Artifact Root). Title is `<Name> - Business Requirements` (matching the H1; no conventional-commit prefix). Keep the doc light and standalone-readable: a Goal Capsule (objective, product authority, open blockers) and the Product Contract. Do **not** emit a Goal Launch Block or Reader Index. See `references/brainstorm-sections.md` — which owns the artifact content rules, including repo-relative file paths inside the doc.

**Ready for Planning Check.** After writing the actual file, run the four checks in `references/brainstorm-sections.md`: Complete, Consistent, Focused, and Usable by planning. Fix failures in place when the correction preserves settled intent, then rerun the failed checks. If a correction would choose or change product behavior or scope, ask one targeted question, update the artifact after the answer, and rerun the checks. Do not declare the artifact written or enter Phase 4 while any check fails. When confirming in chat after the pass, report the artifact with its absolute path so the reference is clickable.

#### Vocabulary Capture — after the business requirements document (only if CONCEPTS.md already exists)

**Skip this step entirely if `CONCEPTS.md` does not exist at repo root** — creation is owned by a separate vocabulary-maintenance workflow, if you have one.

Run this **after** the approaches, the scope synthesis, and the business requirements document — that is where the canonical term often gets chosen or corrected, so capturing during early dialogue (before this point) would miss the final resolved name. If it exists, scan the full dialogue and the Product Contract for **resolved** domain terms — terms where the conversation actively pinned down a precise local meaning, not terms merely mentioned in passing. **Resolved means the definition is settled, not still under discussion.** Provisional terms that may still revise stay in the conversation only.

For each resolved term: if missing, add it; if present but new precision surfaced, refine it; if already consistent, no action.

**Domain entities, named processes, and status concepts with project-specific meaning only.** Not file paths, class names, function signatures, or implementation decisions — `CONCEPTS.md` is a glossary, not a spec or catch-all.

Follow the format set by existing entries. Apply edits silently. (If Phase 3 skipped the doc, still run this against the resolved dialogue.)

#### Grill gate — after the business requirements document, before the closing summary

The document is written first, then interrogated. A written Product Contract is something the user can falsify; a dialogue still in flight is not. Ask before the gate, per `pipeline` → "Asking before a transition". Skip: do not run `grill-me`, do not set `grilled:`, say so in the closing summary, and go on to it. Stop: end the turn. Run:

1. **Run `grill-me` on the written document.** Load that skill (Skill tool, or read `grill-me/SKILL.md`) and follow it. Do not summarize it and do not invent a shorter interview.
2. **The frontier decides the length, not a quota.** This phase already ran the pressure test and the blindspot pass, so a run that settled everything cleanly has an empty frontier and the gate closes in one turn. That is a pass, not a skipped gate.
3. **Apply what the grill reversed in place**, in this same document — a reversed decision replaces the line it contradicts rather than sitting beside it. Re-run the Ready for Planning Check over anything the grill changed.
4. **Record it in the frontmatter** — `grilled: YYYY-MM-DD` — so a later session can tell the gate closed without replaying this conversation. See the `doc-versioning` skill for the field.

A paused run that never reached a document skips this gate: there is nothing settled to interrogate. Say so in the pause summary.

### Phase 4: Closing Summary

Once the business requirements document is written and its grill question has been answered (or the run ends without a document — brief alignment only), display a closing summary.

After the grill ran, the summary includes what it changed; after a skip, it says the grill did not run. Then read `pipeline` and ask about the stage its table names after this one, per "Asking before a transition". A run with no document to grill asks about that stage the same way. Do not list every remaining stage, do not skip to architecture or implementation, and do not start the next stage without a yes.

Use absolute paths for chat-output file references — relative paths are not auto-linked as clickable in most terminals.

When a document was written, display:

```text
Requirements captured.

Document: <absolute path to the business requirements document>

Key decisions:
- [Decision 1]
- [Decision 2]

Grill: [what it changed, or "frontier was empty — nothing left assumed"]
```

If the user pauses with open items still unresolved, display:

```text
Brainstorm paused.

Document: <absolute path to the business requirements document>  # omit line if no artifact was created

Still open:
- [Open item 1]
- [Open item 2]

Resume with `brainstorm` to pick this back up.
```

When no document was warranted (brief alignment only), skip the "Document:" line and summarize the decisions reached in the conversation instead.
