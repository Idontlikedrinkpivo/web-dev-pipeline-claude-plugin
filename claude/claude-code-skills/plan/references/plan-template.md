# The plan document

Read at Step 7, before settling: the file `doc-typist` renders from the
settlement, and the pins it carries. The unit block itself is
`SKILL.md` → Step 4.

## Pins

Pin what the plan was built from as `path@<version>`, the version already
written in each source file. Do not mint a version to make the pin current:

```yaml
sources:
  - documentation/architecture/architecture.md@1.1.0
  - documentation/architecture/domain.md@1.3.0
  - documentation/architecture/scenarios/invoices/01-invoices.md@1.3.0
  - documentation/requirements/srs/srs.md@1.3.0
  - documentation/api/openapi.yaml@1.3.0
  - documentation/db/schema.md@1.2.0
```

Pin the OpenAPI root and the schema whenever they exist: a plan built on
an operation or a column that later changed is otherwise never seen to be
stale.

## Template

```markdown
---
name: implementation plan <version>
date: YYYY-MM-DD
sources:
  - documentation/architecture/architecture.md@<version>
  - documentation/architecture/domain.md@<version>
  - documentation/architecture/scenarios/<area>/<group>.md@<version>   # one per SRS group in scope
  - documentation/ui/screen-specs/S-1-<screen>.md@<version>           # one per screen in scope
  - documentation/requirements/srs/srs.md@<version>
  - documentation/api/openapi.yaml@<version>                          # when it exists
  - documentation/db/schema.md@<version>                              # when it exists
routing: executor-catalog
---

# План реализации: <version>

## 1. Кратко
Version · level · reason (Step 1) · the changes, when several · architecture
level and budget · stack · the unit spine this produced · what the scaffold
already provides.

## 2. Карта юнитов
| U | Юнит | Сложность | Исполнитель | Вложенный | Зависит от | Параллельно |
|---|---|---|---|---|---|---|

Then, when useful, a D2 dependency graph of the same table at the
packet's DIAGRAM PATH (`diagrams/deps.d2` plus the rendered `.svg`).

## 3. Юниты
One `### U<n>.` block per unit, per Step 4.

## 4. Волны
Which units may run together, derived from «Зависит от» + «Параллельно». A wave
is a claim about contention, so name the contention that keeps units apart.
For each wave, also name which use case (UC id) first runs end-to-end after
it, or `—`.

## 5. Критерии готовности
The plan-wide gate: lint contracts from the foundation §6 pass, the end-to-end path
runs, every quoted invariant row has a test, every AC is covered.
```
