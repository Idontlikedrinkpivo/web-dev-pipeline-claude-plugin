# Output template — domain model (`documentation/architecture/domain.md`)

Read this when writing or editing the domain model (mode `domain`). Use
these sections in this order; skip an empty one with a single line
saying why. This is the **only** home of every business rule: the
invariant table lives here and nowhere else. Scenarios cite its rows by
rule id; the foundation maps its named errors to HTTP.

The notes under each heading are writer instructions, not text to copy.
How to design an entity, row shapes of the invariant table, value
objects, when anemic is fine: `rich-entities.md`. `<версия>` is the open
iteration's service version (`0.1.0` on greenfield); each pin names the
version of the source it was read at.

```markdown
---
version: <версия>
updated: YYYY-MM-DD
sources:
  - documentation/requirements/srs/srs.md@<версия SRS>
  - documentation/db/schema.md@<версия схемы>
  - documentation/architecture/architecture.md@<версия фундамента>
---

# Доменная модель: <система / фича>

## Журнал изменений

| Версия | Дата | Изменение | Тип | Кого затрагивает |
|---|---|---|---|---|
| <версия> | <дата> | первый выпуск | — | — |

## 1. Объекты-значения
Без вступительного абзаца. Таблица или по подзаголовку на тип: Тип ·
Файл (`domain/…`) · Правило на входе (SRS id) · Эскиз сигнатуры.
Мелкие типы с одним правилом на входе, своего id нет. Правило
`from(raw)` видно в сигнатуре, не пересказывать прозой. Календарная
граница («день», «квартал», «через N дней») — метод объекта-значения,
никогда не `Clock`.

## 2. Сущности
Заголовок — `### <Name> (сущность) — \`<root>/<area>/domain/<file>.<ext>\``,
с настоящим расширением стека. Под заголовком одна фраза «что это» и
эскиз в TS-подобной нотации (поля, состояния, методы, которые
отказывают; `create`, `reconstruct` — «восстанавливает из БД как есть,
без повторной проверки create»). Кто какой код статуса может поставить —
методами, не полным перечнем кодов (коды — атрибут `status` схемы, подписи —
колонка `label` той же таблицы). Под эскизом одна строка `Поля также в:` —
пути к модели хранения, мапперу, моделям чтения и wire-схеме, производные
с пометкой `(генерируется)`.

## 3. Именованные ошибки
Таблица: Ошибка · Поднимает (метод сущности / VO, или шаг сценария для
`…NotFound` / `Forbidden`) · Когда · Правило (SRS id). Здесь — каждое имя,
которое могут вернуть сценарии; сценарии их не переопределяют. Статус HTTP
не писать — он в фундаменте, §4.

## 4. Инварианты
Таблица без вступления и без абзаца под ней: Правило → Владелец → Где
проверяется → Ограничение в схеме (`none` / `CHECK` / `UNIQUE` / `FK`) →
Исход. Ячейка «Правило» начинается с id из SRS (`BR-3: …`), дальше слова
требования. Схему пишет колонка «Ограничение в схеме», тесты — «Где
проверяется»; это правило писателя, в файл не копировать.

## 5. Проверки границ
Только если есть. Таблица Правило → Форма → Доказательство, без абзаца
«зачем отдельная таблица». Сюда же строка: сценарий не отдаёт сущность в
HTTP (или решение отдавать, со ссылкой на строку «Ключевых решений»
фундамента).

## 6. Что не сущность
Сами факты, строкой на существительное из SRS, которое не стало
сущностью: чем оно стало (объект-значение, модель чтения, колонка, внешний
справочник) и почему. Без фразы «иначе писатель заведёт пустые сущности».

## 7. Глоссарий → типы
Таблица: Термин SRS (дословно) · Тип · Где (`domain/…`, модель чтения
области, внешний). Один термин — один тип; синоним из SRS — строка,
указывающая на тот же тип.
```

## Column rules of the invariant table

These stay in the skill; the file never glosses them.

| Правило | Владелец | Где проверяется | Ограничение в схеме | Исход |
|---|---|---|---|---|
| SRS id first, then the requirement's words, capital first letter; column is «Правило», never «Правило (цитата)» | type that holds the data | method or constructor that refuses, same signature as in the sketch | `none` / `CHECK` / `UNIQUE` / `FK`, copied from the schema document | named error (from §3), resulting state, or derived value |

- «Где проверяется» is always an entity or value-object method. Never a
  use case, controller, adapter, `Clock`, or the word `database`.
- «Ограничение в схеме» copies the schema: `CHECK`, `UNIQUE`, or `FK` when
  that document created the constraint, `none` when it left the rule to
  the entity. Do not add a constraint the schema does not have.
- Assumed rows tag `(A-n)` and point at
  `documentation/architecture/open-questions.md`.

## Where each BR lands

Every `BR-n` of the SRS lands in exactly one place, its id first in the
cell: a row of §4 (domain rule), a row of §5 (boundary rule), or the
«Доступ» row of the scenario that guards it (access policy — in the
scenarios document of that area). A BR left only in prose, in a
scenario's Ошибки, or in an adapter is lost to the tests.
