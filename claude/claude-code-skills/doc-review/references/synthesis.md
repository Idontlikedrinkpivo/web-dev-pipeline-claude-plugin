# Synthesis

Run after every dispatched reviewer returns. Order matters.

## 3.1 Validate

Read each reply by the field names of `findings-format.md`. Drop a finding
that misses a field or uses a value outside its list, and note the persona
as `malformed` in Coverage.

A reply that is not in the format at all:

- it plainly says there is nothing to report → read it as `findings: none`
  and note `format` against the persona in Coverage;
- it carries findings in free prose → dispatch that persona once more with
  the same packet and the line "Return only the findings text in the
  required format"; a second free-prose reply → `malformed` in Coverage, and
  the report names that persona's check as not done.

Do not rebuild findings out of prose yourself, and do not narrate validator
diagnostics to the user.

## 3.2 Confidence gate

| Anchor | Route |
|---|---|
| `0`, `25` | Drop. Footnote `Dropped: N` under Coverage when N > 0 |
| `50` | FYI. No walk-through, no bulk action |
| `75`, `100` | Actionable — classify by `autofix_class` |

## 3.3 Deduplicate

Fingerprint: `normalize(section) + normalize(title)` (lowercase, strip
punctuation, collapse whitespace).

Matching across personas, same direction: merge. Keep highest severity,
highest anchor (tie → earlier in document order), union evidence, list
all agreeing reviewers. Attribute Coverage to the highest-anchor persona.

Opposing recommended actions: do not merge — send to 3.5.

## 3.3a Prior rounds (round 2+ only)

Match each finding against the decision primer by
`normalize(section) + normalize(title)` **and** more than half overlap
with the primer's `Evidence:` snippet.

- Matches a Skip / Defer → drop it. Coverage note:
  `previously rejected, re-raised`. Exception: the quoted evidence no
  longer appears in the document — the section changed; keep it as new.
- Matches an Applied finding with overlapping evidence → the fix did not
  land. Report it under `Fix did not land`, not as a new finding.
- Matches an Applied finding and only says it landed → drop, Coverage
  `Verified: <title>`.

Synthesis is the authoritative gate here: a persona may re-raise despite
the primer, and the user already decided that finding once.

## 3.4 Agreement promotion

Two or more independent personas on the same merged finding: promote
anchor one step (`50 → 75`, `75 → 100`). Note `(+1 anchor)` on the
Reviewer cell.

## 3.5 Contradictions

Personas disagree on the same section: one combined finding, `manual`,
`error`, framed as a tradeoff — not a verdict.

## 3.6 Recommended action

One field per merged finding, most conservative first:
`Skip > Defer > Apply`.

- `safe_auto` / `gated_auto` → Apply
- `manual` with a concrete `suggested_fix` → Apply
- `manual` tradeoff / scope question with no recommended resolution → Defer
- Contradiction that says "keep as-is" → Skip
- Apply without a `suggested_fix` → downgrade to Defer

Routing and bulk actions read this field. They do not recompute it.

## 3.7 Apply `safe_auto`

Apply `safe_auto` findings at anchor `75` or `100` silently, in document
order, one edit pass. Re-read the file before writing if the user may be
editing it. List every applied fix in the report.

Do not silently apply `gated_auto` or `manual`.

## 3.8 Present

Render the report from the skill's report shape. Then, in interactive
mode, follow `routing.md`. In non-interactive mode, return the remaining
`gated_auto` / `manual` / FYI findings as structured text and stop with
"Review complete."
