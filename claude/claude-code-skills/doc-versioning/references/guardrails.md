# Stamp checklist

`doc-versioning` runs this once per dirty contract document (SRS, OpenAPI,
DB schema, architecture foundation, domain model, scenarios, screen specs)
when the user invokes this skill.
`plan` does not call it. Writers, gates, and `work` do not run this
list: they leave `version`, `updated`, and the changelog as they found them.

The diff is the file about to be committed against HEAD. A file git has
never had keeps its single «первый выпуск» row at the iteration's version,
with its date set; do not add a second row.

**Before any file**

- [ ] The iteration's version is the open `plans/<version>/` (no `summary.md`); none open → opened per `pipeline` → Service version, on the user's answer — When a version is born

**Every document in the commit**

- [ ] One canonical file for this system, at its unchanged Registry path (no date, no topic) — Which mode am I in · Registry · One folder per document
- [ ] An unversioned row got no `version`, no changelog, no typed row — Registry
- [ ] Plan: a closed version's folder untouched. DB: a new numbered file in `db/migrations/`, no committed one edited, and `migration:` names the newest file — `references/exceptions.md`
- [ ] Every cited token the diff against HEAD touches is typed ломает / добавляет / уточняет / no row; an explanation of an existing token is no row — What a version is · `references/change-types.md`
- [ ] No id renumbered, reused, or deleted without an `удалён:` note — ID stability
- [ ] Every pin read: stale ones (a «ломает» after the pin) carry the banner; pins behind by «уточняет» only are refreshed — Staleness and cascade
- [ ] The diff contains only what the feature touches — Increment discipline
- [ ] Any contradiction with an existing requirement was decided by the user — Increment discipline
- [ ] No live `operationId` broken without a «ломает» row; with external consumers, only under a new API major — Increment discipline

**No change got a row** — then commit the body as it is:

- [ ] `version`, `updated`, and the changelog stay exactly as HEAD had them — When a version is born

**At least one row** — stamp, then commit that stamp with the body:

- [ ] `version` is the iteration's version (OpenAPI with external consumers: the contract's next SemVer); `updated` is today — When a version is born
- [ ] `grilled:` and `reviewed:` stay as the working copy had them. An SRS has no `status`, `grilled:`, `reviewed:`, or `sources` — do not add them — Frontmatter
- [ ] One row per changed cited token or tight group, newest first, `Версия` matching `version`, no placeholder in any cell; a token already rowed in this version has its row amended, not duplicated — Changelog · `references/changelog.md`
- [ ] Every «ломает» row's `Кого затрагивает` holds a verdict per downstream consumer; every «добавляет» row names where the new thing lands — Staleness and cascade
- [ ] No row per correction pass — When a version is born
