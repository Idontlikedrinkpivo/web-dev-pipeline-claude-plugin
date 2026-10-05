# Changing the catalog

Read this only when you add, retire, or re-point a row. Dispatching a row does
not need it.

- **Re-point a tier** — change only the `model:` (or `effort:`) line of
  `_agents/<name>.md`, after reading `model-economics.md`, and fix that page in
  the same edit if it no longer reads true. Nothing in the catalog table or
  downstream moves. The plugin or the installed link picks the change up after
  `bash claude/sync.sh` and `claude plugin update dev-pipeline@dev-pipeline-marketplace`;
  a running session needs a restart.
- **A new row needs a dispatcher and an agent file, not a unique model.**
  Fill `Dispatched by` with the skill and the moment it fires, and add
  `_agents/<name>.md` (frontmatter `name`, `description`, `model`, `effort`,
  and `tools` when the row is read-only; a short body — see the existing
  files), list it in `.claude-plugin/plugin.json` → `agents` (the plugin loads
  only the files listed there; `install.sh` warns when one is missing). Two
  rows may share a model when their packets differ; no row may exist without a
  skill that names it. A row nobody dispatches is deleted, not kept "for
  completeness": an unreachable row reads like an option and quietly never
  gets used. Example: `test-lite`, `test-medium`, and `docs-lite` were deleted
  because tests are written by the unit's own implementer (TDD is the order
  inside a unit, never a separate executor) and a docs unit is transcription.
- **Add a branch** (e.g. a `perf` or `migration` row) — add the row and say in
  `Runs` what distinguishes it from the tier's `code` row, otherwise plans will
  never choose it. A `docs-review` row is chosen by `doc-review`, not by
  `plan` — name the personas in **Document-review routing** or they will keep
  resolving to the old executor.
- **Retire a name** — keep the row and its agent file, with the replacement
  named in `Runs`, until no plan under `documentation/plans/` still cites it.
  Old plans must stay executable. When the row goes, delete its agent file and
  its line in `.claude-plugin/plugin.json`.
- **Do not add a fifth complexity tier.** Grades come from the cascade, which
  has four. A new tier without a matching cascade rule cannot be assigned.
