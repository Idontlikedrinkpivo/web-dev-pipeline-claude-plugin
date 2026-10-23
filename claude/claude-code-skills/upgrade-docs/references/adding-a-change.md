# Adding a change to changes.json

Add a row when a release changes what files the pipeline already wrote in a project should look like: a new
document or stage whose output older projects lack, a new section in a document, a new rule for existing text, a
renamed folder, a generated artifact that must be rebuilt. Not for a change inside a skill that leaves the
project's files as they are (wording, a gate, an executor, a model) — those take effect on the next run by
themselves.

## The row

```json
{
  "id": "api-descriptions",
  "version": "1.2.134",
  "title": "Описания в контракте API — для того, кто вызывает API",
  "what": "One or two plain Russian sentences: what the plugin does differently now.",
  "applies": {"exists": "documentation/api/openapi.yaml"},
  "behind": {"grep": {"path": "documentation/api", "pattern": "Порядок проверок|NFKC"}},
  "fix": "The skill and its reference that make the change, and exactly what to do — one step or the whole stage."
}
```

- `kind` — `"code"` when the change touches the project's code or settings (linter and CI config, a project
  skill, `.claude/settings.json`): `upgrade-code` makes it, with the project's checks around it. Leave it out for
  a document change, like the row above — `upgrade-docs` makes those.
- `id` — stable, kebab-case; a project's stamp lists skipped ids, so never rename one.
- `version` — the release that brings the change (the version `sync.sh` is about to print).
- `applies` — true only for projects that have the thing at all: no API, no API rule.
- `behind` — true while the project lacks the change, false once it is made. It is the check the upgrade skill
  runs after the fix, so it must turn false when the fix is done, and stay false on a project written by the new
  release. Try it on a project written before the change and on one written after (the room-booking fixtures, a
  real project).
- A later change that supersedes an earlier one replaces it: one row, the later version, a check for the final
  form.

## Checks

`{"exists": path}`, `{"missing": path}` (a path with `*` is a glob — `*/skills/verify/SKILL.md` finds the
project skill under `.claude/` and `.agents/` alike), `{"grep": {"path": file or folder, "pattern": regex}}`,
`{"all": [...]}`, `{"any": [...]}`, `{"not": check}`. Paths are relative to the project's root. A grep reads
text files (`.md .yaml .yml .json .txt .sql .dbml .html`) under a folder, or every file a glob path names, whatever
its type (`*/Dockerfile`, `*/src/bootstrap/*` — keep globs to fixed depths: `**` walks `node_modules`); the pattern is
a Python regex in multiline mode. Prefer a sign that only the old format has — a heading it used, a word the new rule forbids —
over a sign of the new one; and keep it away from text where the old word is legitimate (a changelog, a quote).

Check by hand: `python3 upgrade-docs/scripts/project_format.py list <project>` on both projects.
