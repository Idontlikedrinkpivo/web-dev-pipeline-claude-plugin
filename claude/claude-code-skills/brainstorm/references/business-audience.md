# Business requirements for customers and downstream authors

This is the default presentation contract for every brainstorm business requirements
document. It takes precedence over fixed English headings, visible protocol codes
and generic rendering examples in other brainstorm references. SRS and plan formats
stay unchanged. The same Markdown serves the customer and downstream authors;
non-rendered semantic comments preserve the latter's identities and links.

## Organize around the reader's work

Use headings in the customer's language, named for the product and its actual
capabilities: purpose, users, capabilities grouped by business topic, data,
scenarios, expected behavior, scope and material dependencies. For example,
«Зачем нужен помощник», «Кто будет пользоваться», «Пересчёт сроков».
Goal Capsule and Product Contract describe semantic roles, not mandatory headings.
Do not add empty sections, a separate index or repeated Key Decisions merely to
satisfy a template. Keep a decision's rationale next to its owning requirement.

Start with a brief orientation: what the product does, for whom, what is agreed,
and what still needs a decision. If questions remain, say that this is a document
for agreement and that proposed options are not approved behavior. State which
unknowns block the next stage and which are deferred. This is prose for the reader,
not a new status/frontmatter protocol. A polished document is not automatically
ready for SRS.

Group short requirements by business capability. Use compact tables for uniform
requirements; keep explanations and long questions outside table cells. Write
what the user or product does in ordinary words. Explain unfamiliar terms when
first used, without stripping domain precision or changing agreed thresholds.

Keep stable R/A/F/AE/OQ identities through restructuring. Use ordinary visible
numbers or descriptive headings with IDs in comments. Preserve an established
customer number; do not introduce a separate interview-round number. When moving
requirements, choose a presentation order that is understandable within each group;
do not renumber stable identities simply to make a sequence consecutive. Never
silently drop an identity, dependency or unresolved decision.

## Stable metadata

```markdown
<!-- ce-section: requirements -->
## Что должен делать помощник

### Пересчёт сроков

| № | Требование |
|---|---|
| 1 <!-- ce-requirement: R1; open: OQ-7 --> | Пересчитывать сроки задач с учётом зависимостей. |
```

Section roles: goal-capsule, summary, actors, requirements, key-decisions,
key-flows, acceptance-examples, scope-boundaries, dependencies-assumptions,
sources, work-relationships. Use those that apply. ce-actor carries A-ID;
ce-flow carries F-ID and covers links; ce-example carries AE-ID and covers links.
ce-decision carries governed R-IDs, session-settled class, rejected alternative
and rationale. Preserve these facts when moving visible annotations to comments;
an editorial rewrite never creates settlement.

Readers discover semantic comments first, but accept legacy English headings
and visible prefixes. Descriptive links should make sense without knowledge of
the IDs. Do not print traceability code lists on each requirement.

## Questions next to the relevant topic

Keep the authoritative text in adjacent open-questions.md. Each long question
has a ce-question marker followed immediately by its heading and full text:

```markdown
<!-- ce-question: OQ-7; class: Отложено; source: discussion, YYYY-MM-DD -->
## Вопрос 7. Какие данные использовать для пересчёта сроков?

Процент выполнения не показывает, остался один день или две недели.
Например, задача выполнена на 50%, но оценка оставшегося времени неизвестна.

**A. Брать оценку исполнителя.** Потребуются актуальные оценки оставшегося времени.

**B. Строить прогноз по прогрессу.** Потребуется согласовать правило расчёта;
при неравномерной работе прогноз может заметно меняться.
```

A material choice explains: what needs deciding, a concrete situation, options
and the practical consequences of each. Add a recommendation only when there
are grounds; label it as proposed until accepted. Options that require data
state what data is needed. Examples illustrate a decision; they are not new
requirements. Do not manufacture options for factual input such as file formats,
used repositories or portfolio size: ask for that information directly and give
an answer format when helpful.

For a customer agreement document, put the relevant questions after their owning
topic instead of requiring constant navigation to another file. Generate their
text; never maintain two editable copies. Insert this empty include at the desired
location, with the heading level appropriate for that section:

```markdown
<!-- ce-question-include: OQ-7; level: 4 -->
<!-- /ce-question-include -->
```

Run `python3 "<brainstorm skill folder>/scripts/question_projection.py" <document>`.
The script replaces only include bodies from open-questions.md. Refresh after any
question change or resolution; check with the same command plus --check before
presenting, reviewing or committing. Edit the canonical block, not generated text.
Preserve the OQ-ID for an answered question and record its answer in that block;
apply the settled outcome to the owning requirement and remove obsolete options.
Missing/deleted source IDs fail validation rather than leaving a stale projection.
Legacy question tables remain readable input; convert referenced questions into
marked blocks before using includes. Conversion preserves IDs and classifications.

Include each full question once, at its primary topic; elsewhere use a descriptive
link. Cross-cutting questions can live in a final shared section. For a short
settled document with little to clarify, descriptive links alone are sufficient.
No padding, duplicate question register, or mandatory quota of questions.

## Scenarios and expected behavior

Write a short situation, the user's action or triggering event, and the observable
result. Avoid unexplained field labels and sequences of IDs. For example:

```markdown
<!-- ce-flow: F1; covers: R1; open: OQ-7 -->
### Увидеть пересчитанные сроки

После обновления сведений о задачах пользователь просматривает новый прогноз.
Помощник учитывает зависимости задач; способ расчёта оставшегося времени ещё
требует согласования в вопросе 7.
```

An acceptance example needs an observable expectation; a restatement of the
capability is not proof it is testable. Do not invent expected dates, formulas or
behavior to fill a gap. Mark examples dependent on unresolved decisions as
incomplete and preserve the corresponding links. Keep confirmed examples precise.

## Before finishing: reader and source checks

Read the rendered document without relying on comments. Can a customer identify
what the product does, find the topic, understand every term necessary for a
choice, distinguish options by consequences, and see what remains unapproved?
If not, revise the wording or ask for missing product information. This is a
required readability check in addition to brainstorm's Ready for SRS Check.

Then inspect the source: every previous requirement, actor, flow, example,
dependency and question retains its identity and meaning. Validate generated
includes with --check and check links. Neither options nor recommended answers
may appear as settled behavior in requirements or examples. A missing required
product decision blocks Ready for SRS even when labelled «Отложено»; the label
alone does not make it safe to proceed. If other scope can proceed independently,
state its boundary and obtain agreement rather than silently shrinking scope.
