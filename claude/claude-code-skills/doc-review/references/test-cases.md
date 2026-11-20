# Reviewing a test-case set

The set `documentation/ui/test-cases/` (`ui/<product>/test-cases/` with several UI products) is one document: its
`README.md` and the section files `NN-<slug>.md`. A path to any of its files resolves to the folder. Two scripts
already proved the mechanics at the stage's close — every trace resolves, every acceptance criterion has a case or
a «Без интерфейса» line. This review asks what they cannot: does each case prove what it claims, can a test walk
it, and does the set leave out a state, a boundary or a role that the documents give.

## Before the dispatch

1. **The two scripts, as convention checks** (SKILL.md → Convention checks, step 3). Each `✗` line they print is
   a convention miss, P1, Reviewer `convention`; `check_trace.py`'s warnings are not, so it runs with `--quiet`:
   `python3 "${CLAUDE_SKILL_DIR}/../ui-test-cases/scripts/check_trace.py" --docs documentation --quiet` and
   `python3 "${CLAUDE_SKILL_DIR}/../ui-test-cases/scripts/check_coverage.py" --docs documentation`.
2. **The hints.** `design-lens-reviewer` runs
   `python3 <skills_root>/ui-test-cases/scripts/spec_coverage.py --docs documentation` itself: the rows of the
   screen specs («Состояния экрана», «Ошибки ответов») no case names. A hint is not a finding until the reviewer
   finds no case for the row under another name.
3. **The scope** — which section files the reviewers read:
   - no `reviewed:` in README's frontmatter (the first review): every section;
   - with `reviewed:`: the sections changed since that date —
     `git log --since=<reviewed> --name-only --format= -- <folder>` — plus every section of a screen whose spec
     changed since then; README always;
   - round 2 and later: the sections the writer changed in this review;
   - the user may name the whole set or sections.

   Before the dispatch, say the scope in one line: the sections, their cases, the parts (below).

## The team

Fixed on this type; the conditional table of SKILL.md → Select personas does not apply.

| Persona | Runs | Reads |
|---|---|---|
| `coherence-reviewer` | always, once per part | the part's sections whole; README's «Как читать кейс», roles and data |
| `feasibility-reviewer` | always, once per part | the same |
| `design-lens-reviewer` | always, once | the screen specs, README's tables, the hints; sections by `grep` |
| `security-lens-reviewer` | when the SRS names more than one role or an authorization exception (an `Exc` with a forbidden outcome) | the SRS roles and exceptions, the specs' Forbidden states, README; sections by `grep` |

`product-lens-reviewer`, `scope-guardian-reviewer` and `adversarial-document-reviewer` never run here: what to
build was settled in the SRS, and the set transcribes it into checks.

**Parts.** Coherence and feasibility read every case of their scope, which runs to megabytes in a large set. Group
the section files in order, adding files while the part stays under 300 KB (`wc -c`); each part is one dispatch
per persona, and `{document_files}` lists README plus that part's sections. The design and security lenses get
README plus every section in scope as one dispatch: they look across the set and read cases only where a check
leads them.

## Apply goes to the writer

The session edits no file of the set, not even a `safe_auto` fix: a case's trace ties it to the step table, the
element numbers, the frames and the operations, and a hand edit leaves it pointing at the old ones
(`ui-test-cases` → Mode write). So:

- synthesis step 3.7 does not edit: the `safe_auto` findings join the applied list;
- an applied finding (`references/routing.md` → Apply) is added to that list, its section named;
- after the last finding, the session dispatches `ui-test-writer` once, `MODE increment`, with the list in
  `TO FIX` (`ui-test-cases/references/writer-prompt.md`), then runs both scripts again, as the stage's close
  does;
- a finding that needs a spec, an SRS or an API change is not the writer's: it is a decision for its owner's
  stage (`pipeline` → `references/decision-changes.md`), and the case waits for it in the set's gaps.

The report's «Внесённые правки» names what went to the writer; a fix that did not land in the writer's report is a
row of «Правка не применилась» in the next round.

## Closing

`reviewed: <today>` goes into README's frontmatter. The set has no version: the stamp is the date the next review
counts changed sections from.
