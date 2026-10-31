---
name: srs-writer
description: >-
  Turns a product or feature description into the numbered SRS (FR, NFR, BR, UC, Given/When/Then) or updates it. Use
  for «напиши ТЗ на фичу», «оформи требования», «добавь требование». A screen with mockups: screen-spec.
---

# SRS Writer

Turns already-settled product decisions into a **Software Requirements Specification** — the formal document that sits between "what we decided to build" (`brainstorm`) and the schema and API that are written from it. Architecture reads those later, when it lays out the code.

**This skill does not invent product decisions.** It reads whatever the user gave — a file in any format, a paste, or a description in the chat — and:
1. Extracts the settled product shape and systematizes it into IDed, unambiguous requirements.
2. Adds the sections a short description usually omits: Non-Functional Requirements, Business Rules/Invariants, and full Use Cases with main/alternative/exception flows.
3. Attaches a Given/When/Then acceptance criterion to every scenario.

A short, messy, or differently headed description is still input: write the SRS from it, and put what it does not say in `open-questions.md` beside the file. This skill formats and completes; it does not decide.

## Orchestrator (session)

The session writes no SRS file. `srs-author` settles it and nests
`doc-typist` to print it. A report whose `DELEGATED` is not `doc-typist`
comes back until it is.

1. Resolve the source (Input Resolution, steps 1–4). From `upgrade-docs` for a running system without an SRS: `MODE as-is`, the source is the code and the project's own documents, and no iteration is opened (`upgrade-docs/references/as-is.md`). Only when there is no file, no description and no business-requirements document (Input Resolution, step 3), route to `brainstorm`. Do not invent the product.
2. **Be in the iteration before the dispatch** (not in `MODE as-is` — step 1): reuse the open one, or open it as `pipeline` → Service version says (it owns the steps, the number's question — MAJOR is proposed when the increment adds a new capability group to §3 — and the script's exits, asked before anything else). A new project — `documentation/` did not exist when this stage started — also runs `python3 "${CLAUDE_SKILL_DIR}/../upgrade-docs/scripts/project_format.py" born .` and commits `documentation/.dev-pipeline.json` with the document (the script's `born` line says why). Put the version in the packet's `VERSION`. A greenfield SRS is born at it; an increment leaves `version` to the stamping commit.
3. Read `executor-catalog`. Dispatch exactly one writer with `executor-catalog/references/srs-writer-prompt.md`. Fill `READ FROM DISK` with the source's path when it is a file — and on an increment `srs.md` and every `areas/*.md` — and `SOURCE TEXT` with only what is on no disk: the source when it exists only in the chat, and the user's answers (`executor-catalog` → Dispatch contract, «Paths, not pasted documents»). The executor is `srs-author`. Before the `Agent` call, write `srs-author | dev-pipeline:srs-author`, then dispatch `subagent_type: "dev-pipeline:srs-author"` with no `model`: the agent file holds it. A dispatch on `general-purpose` or with a typed `model` is a failed dispatch. A missing agent or a rejected alias is a stop per the catalog's Dispatch contract and Slug hygiene. Do not write the file on the session model to save a dispatch. A failed dispatch is reported, not replaced.
4. On `STATUS BLOCKED` for a product decision, ask the user (options go through `pipeline` → `references/question-format.md`), then dispatch `srs-author` again with the answer pasted. Do not fill the gap yourself.
5. **Grill gate — after the file exists, before it is declared done**, because `grill-me` works against an artifact.
   1. Ask first, per `pipeline` → "Asking before a transition". Run: read `grill-me` and follow it. Skip: name it in the report and ask about `doc-review`. Stop: stop.
   2. Grill what this stage settled — NFRs, invariants, use-case flows, exception paths, the security sub-checklist. Not the interface: a question about screens, controls or wording belongs to the mockups (`ui-design`). Decisions that arrived already grilled with the business-requirements document are not re-litigated. Increment mode grills the new feature only.
   3. Stop after each round and wait. The rounds only fill the grill's ledger; the session does not edit the file.
   4. When the user confirms the close, dispatch `srs-author` **once** with `MODE grill-reversal`, every reversal from the ledger in `REVERSALS` and every deferred question in `DEFERRED` — one dispatch, not one per round, so no half-grilled SRS is printed in between (the writer's side: Grill reversals). No reversal and nothing deferred — no dispatch.
6. After the grill closed or was skipped, ask about `doc-review` the same way — never before: whatever brought the SRS here (greenfield, an increment, a decision changed, a resumed session), `doc-review` is not offered until the grill question was asked and answered in this iteration. The stamp commit names both gates (`docs: SRS <version> · grill: прошёл | пропущен | не запускался · review: прошёл | пропущен | не запускался`), so a later session reads them from `git log`: `пропущен` is the user's B on the gate's question; `не запускался` is a gate whose question was not answered — the user stopped first — and «где я» offers it again. A run or a skip is named in the report. Neither writes `status`, `grilled:`, or `reviewed:` into the file. An SRS handed downstream ungrilled without the user being asked is a failed gate, not a draft; a skip the user chose is not.
7. Report the artifact path, the writer's counts, and what the grill changed, in one line. Then read `pipeline` and follow "Asking before a transition". Do not name a next step from memory.

## Writer (dispatched)

Follow this half only. Do not run `grill-me`, `doc-review`, or `pipeline`.

Read `references/srs-template.md` in full before settling anything: it
holds where the SRS lives and how an increment resumes it, the sections and
ids, the writing rules, the quality gate and the report.

You settle the SRS. You do not print it. When every decision this
template needs is settled, nest `doc-typist` per `executor-catalog` →
Nesting, packet `executor-catalog/references/doc-typist-prompt.md`. A
gap this skill calls BLOCKED returns before that dispatch. Read the
file back. One correction dispatch, then the report. Do not type the
correction, and do not paste the finished SRS into the typist's prompt.

## Scope

**USE this skill when:**
- Any existing description of a product or feature needs an SRS — a business-requirements draft, a note, a ticket, a spec in another shape
- The user states requirements directly, in whatever shape they have
- An SRS for this system already exists and must be updated in place

**NOT for:**
- Deciding what to build, exploring approaches, or resolving open product scope when nothing has been written down — that's `brainstorm`
- Tables, HTTP, layers — `db-schema-design` and `openapi-spec-generator` read this file next; `clean-architecture-design` reads all three later

## Input Resolution

Resolve the source of truth before writing anything:

1. **Explicit path given** — read that file. Headings, language, and format do not have to match this skill's sections.
2. **Text in the chat** — a paste or the recent dialogue. Use it as it is. Do not ask the user to reshape it into the business-requirements shape (`## Goal Capsule`, `## Product Contract`, `R<n>` rows).
3. **The canonical business-requirements document** — `documentation/requirements/business-requirements/business-requirements.md`, written by `brainstorm` in this session or an earlier one. With no path and no chat text it is the source; with chat text it is read too, and the chat adds to it. A business-requirements document is a source, never a reason to brainstorm again.
4. **Nothing at all** — the orchestrator already stopped. If the packet has no source, return `STATUS BLOCKED`. Do not invent the product.

Extract actors, requirements, and scope from the source — the files in `READ FROM DISK` and the text in `SOURCE TEXT`. **Never fill a gap by guessing a product decision.** A missing Actor, an unstated NFR, an ambiguous requirement becomes a row in `open-questions.md` beside the SRS, never a silent assumption and never a section of the SRS. A question the skill says to ask before writing the row (a generic actor, a contradiction with an existing requirement) is `STATUS BLOCKED` with that question as `BLOCKER`. Do not ask the user yourself. Silent-filling here defeats the entire point of a formal spec: a downstream reader (or `clean-architecture-design`) treats every line as decided.

## Grill reversals

Do not run `grill-me`. On `MODE grill-reversal`, apply `REVERSALS` by `grill-me`'s rule (When a pipeline stage invoked this file → the reversals: in place, no bump, no changelog row, an upstream contradiction named — here in `CONCERNS`), and each `DEFERRED` line as an `open-questions.md` row beside the SRS, class `Отложено`. Do not set `grilled:`, `reviewed:`, `status`, or `sources`.

The same mode carries a decision the user changed after the SRS was finished — in `work`, in a later stage, or in the chat (`pipeline` → `references/decision-changes.md`). The session commits that edit at once, still without a version or a changelog row.
