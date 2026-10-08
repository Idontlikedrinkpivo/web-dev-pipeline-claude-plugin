# Cleaning up a closed iteration

Read at the end of the pipeline, after the summary and the tag, before the
last line. Working files pile up iteration after iteration — plans,
progress files, run and audit reports — and an old plan beside the new one
is noise for every later session that searches `documentation/`. This
step clears what the closed iteration no longer needs, once, with one
question.

## What goes, what stays

| In the closed iteration | Fate |
|---|---|
| `documentation/plans/<version>/summary.md` | **stays** — the iteration's numbers and the mark that it is closed |
| the rest of `documentation/plans/<version>/`: `plan.md`, `plan-review.md`, every `progress*.md`, `test-run.md`, `docs-consistency.md`, `security-audit.md`, inventories and other working files | removed |
| `$(git rev-parse --git-dir)/pipeline-work/` files of this iteration's runs (diffs, run reports, stand logs) | removed |
| contract documents — SRS, schema, API, architecture, screen specs, test cases — and everything else in git | never touched here |

Earlier closed folders that still hold more than `summary.md` get the
same treatment in the same question.

**Before removing**, move what only a working file still holds into its
owner document: an accepted risk in `security-audit.md` goes to the
architecture's accepted risks with its reason and date; a decision recorded
only in a run report goes through `references/decision-changes.md`. Nothing
the project still relies on may live only in a file about to go.

## Stray documents

Separately, list files under `documentation/` that are in no row of
`doc-versioning` → Registry and that no document links to — a draft a
session left behind, a duplicate of a canonical file. These are tracked in
git and may matter to someone: never removed with the rest; each is named
with its last commit, and the user decides per file (remove, keep, or move
into the document it belongs to).

## The question

`plans/` is out of git, so what is removed there cannot be restored. Ask
once, per `grill-me` → "How a question is shown": the list with each
file's size and the total, what moved into owner documents, and the
options «A. Удалить рабочие файлы (Recommended)», «B. Оставить». The stray
documents follow as their own questions. Report what was removed in one
line («Убрано: 14 файлов, 2,3 МБ; оставлены summary.md итераций 2.0.0 и
2.1.0»).
