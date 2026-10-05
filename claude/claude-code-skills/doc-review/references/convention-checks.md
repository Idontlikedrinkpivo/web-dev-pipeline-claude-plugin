# Convention checks

Read on the session after the document is read, before dispatch. Each row
is a rule another skill owns — the **Owner** column names it — seen from
the reviewer's side. The rule and its full reason stay with the owner; if a
row and its owner disagree, the owner wins and this row is the one to fix.
The rows are the known cases, not the whole set: a document that breaks
another rule its owner states is flagged the same way, with that section
cited as evidence.

| Check | Owner | When | Broken when | Why |
|---|---|---|---|---|
| Changelog table | `doc-versioning` → Changelog | markdown (`srs`, `db`, `domain`, `scenarios`, `screen`) | no `## Changelog` table immediately after the H1 (on `srs`, `domain`, `scenarios`, `screen`: `## Журнал изменений`), or a leftover `### v…` / table at the end | readers and tools look for the history right after the H1 |
| Architecture changelog | `clean-architecture-design` | `architecture` | no `## Журнал изменений` after `## Описание системы`, or the table sits first after the H1 with no intro, or a leftover `### v…` / table at the end | the architecture skill puts the reader entrance first; the table is still mandatory |
| Version row | `doc-versioning` → Changelog | that table exists | first data row's version cell ≠ frontmatter `version` | the table and the frontmatter must name the same version |
| Row type | `doc-versioning` → What a version is | changelog rows | a `Тип` cell other than `ломает` / `добавляет` / `уточняет` (`—` only on the «первый выпуск» row), or a row that only names comments, `Note`, `description` / `summary` / `example` — that change gets no row | explaining an existing token does not change the contract, and the service level is read from the types |
| Language | `doc-versioning` → Document language | every type | body prose is not Russian. Frozen headings, frontmatter keys, and cited tokens stay as they are | documents are Russian; cited tokens keep their names so citations still match |
| DB notes | `db-schema-design` | `db` | a `Table` without a table-level `Note`, or a column without `note:` | the note is where a table or column says what it means |
| ER diagram | `db-schema-design` | `db` | no `## ER`, or no `diagrams/er.d2` beside `schema.md`, or the section has neither an `.svg` link nor a line that `d2` was missing | projection of the DBML; do not invent tables in-session |
| OpenAPI text | `doc-versioning` → Document language | `api` | `description` / `summary` / `example` not in Russian. `operationId`, paths, and schema names stay English. YAML has no changelog table — do not demand one | same language rule as prose; identifiers are cited tokens |
| Open questions in the body | `doc-versioning` → Открытые вопросы | markdown types | the body has an open-questions heading: `## Открытые вопросы`, `## Open Questions`, `## 9. Открытые вопросы`, `## 4. Open Questions`, `## 6. Open questions`, `## Deferred / Open Questions`, or `### From <date> review` | questions live in `open-questions.md` in that document's folder, not in the contract |
| BRD unversioned | `doc-versioning` → Registry | `business-requirements` | frontmatter has `version:` or the body has `## Changelog` | the draft is not a contract; strip both. Version the SRS |
| Architecture diagram | `clean-architecture-design` | `architecture` | the foundation does not embed the context view in §1, the stores view in §1 «Хранилища», and the layers view in §3 (containers and modules may be a skip line), or an embedded view has no `.d2` in `architecture/diagrams/`, or the document contains a Mermaid fence | the writer emits the D2 projection; do not invent one in-session. A missing `.svg` is a gap only when the section does not already say `d2` was missing |
| Rules scratchpad | `clean-architecture-design` | `architecture` | body has `## Правила по виду` or `### Rules by kind` | writer sort, not a reader section; drop it |
| Deferred body | `doc-versioning` → Changelog | markdown types | a section says "как в 1.1.0" / "без изменений" / "см. историю git" instead of stating its content, or a live heading has an empty body | the changelog carries the diff; the body carries the whole document |
| Interface in SRS | `srs-writer` → Behaviour, not interface | `srs` | an FR, UC step, trigger, or `Then` names a screen, page, button, field, menu, modal, toast, click or tap, a quoted label or message the actor reads, or a colour or layout | the designer must be free to decide the interface; a UI line in the contract forces an SRS edit on every design change. Rewrite as behaviour; the wish moves to `ui-wishes.md` |
| Visual binding | `doc-versioning` → What, not how it looks | `db`, `api`, `architecture`, `domain`, `scenarios` | the document names a widget (button, dropdown, context menu, tabs, checkbox as a control), a presentation (modal, dialog, side panel, toast, banner), layout, density, colour, icon, size, or a layout change at a narrow width — in a row, a state, a `description`, a `Note`, or prose. | the frame decides these by `ux-patterns`; a document that names one must be edited each time the designer decides otherwise. `safe_auto` when the behaviour wording is obvious (`кнопка` → `действие`, `модальное окно M1` → `шаг M1`, `тост «X»` → `сообщение об успехе «X»`); otherwise `gated_auto` |
| Visual detail in words | `screen-spec` | `screen` | a colour, size, border or icon described in words («зелёная обводка», «серый текст») where the frame or variant reference belongs, or behaviour that only a hover cursor describes | the frame is the source of the look; a described look goes stale with the next design edit. `safe_auto` when the row already names the frame: drop the words |
| Cited upstream tokens | `clean-architecture-design`, `screen-spec` | `architecture`, `domain`, `scenarios`, `screen` | a table / column name or `operationId` the document cites does not appear in the DB schema or `documentation/api/openapi.yaml` listed in its `sources:` (strip the `@<version>` pin; read every listed path, not only the first) | architecture and design do not invent tables or operations; a token missing upstream is either a typo or an unrecorded contract change. Suggested fix: retarget to the upstream name, or stop and name the upstream stage that must add it |
| Rule restated | `clean-architecture-design` | `scenarios` | a scenario step states a business rule in words instead of citing its invariant row in the domain model | rules live in one place; a restated rule drifts from its owner. `safe_auto`: replace with the row id |
| Wishes as grounds | `doc-versioning` → What, not how it looks | every type | a finding or a fix measured against `ui-wishes.md` | wishes are input to the design, never a contract — drop the finding |
| Placeholder tree | `clean-architecture-design` | `architecture` | the file tree section has `…`, `<placeholder>` names, or `a\|b\|c` folder alternation | a shape is not a file layout; the writer names real files |

## Which misses may be fixed silently

`safe_auto` only for a
mechanical move of an existing changelog to the table-after-H1 shape, or
for stripping `version` / `## Changelog` from a business-requirements
document. Review-parking leftovers are `gated_auto`: suggested fix is
move the bullets to `open-questions.md` in that document's folder and delete the
leftover heading. A `Cited upstream tokens` miss is `gated_auto` when
exactly one upstream name is a plausible match, otherwise `manual`; never
`safe_auto`. Do not silently retype a row or rewrite prose. Applying a fix
edits the body of the current version. Do not change `version`, `updated`,
or the changelog, and do not add a row. `grill-me` and this review stay
on the last committed version. See `doc-versioning`.
