# The progress file

Read this before creating the progress file (Step 1), when a unit lands
(Step 5.5), and at the close (Step 7). The other stages' progress files
share its shape; which stages keep one is in `pipeline` →
`references/progress-files.md`.

The user follows the run in `documentation/plans/<version>/progress.md`, next
to the plan. It is a view of git, never a source of truth: the `Plan-Unit:`
trailers decide what is done, and a row that disagrees with them is corrected
from git. It is written in Russian. It is not a contract document: no version,
no changelog, no `sources:`.

## The run

````markdown
# Прогресс выполнения плана — итерация <version>

```text
████████████████████████████████████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ 40%
```

Сделано: 8 из 20

| U | Цель | Исполнитель | Статус | Ревью |
|---|---|---|---|---|
| U1 | <goal from the plan> | impl-lite | ✅ закоммичен | COMMIT |
| U2 | … | impl-medium | ⛔ остановлен: <one-line reason> | — |
| U3 | … | impl-hard | ⏳ ждёт | — |

Финальное ревью: <не запускалось | verdict of code-review-full> · BASE `<sha>` · обновлено <YYYY-MM-DD HH:MM>
````

Statuses: `⏳ ждёт`, `🔄 в работе`, `🔍 на ревью`, `✅ закоммичен`,
`⛔ остановлен: <причина>`, `⏭ вне объёма прогона`. Escalations add `(эскалация → impl-critical)` to the
executor cell. The Ревью cell shows the unit review's path
(`FIX_THEN_COMMIT (<что>) → исправлено`, `review-hard ×2: COMMIT`).

Create it before the first dispatch, with every in-scope unit `⏳ ждёт`; on a
resumed run, rebuild it from the unit map and git. Then post its link in the
chat before the first dispatch (`work` → Keep the progress file). It is never
committed — `documentation/plans/` is out of git — so it lives only on this
machine, and git keeps the record through the `Plan-Unit:` trailers. A
pre-existing progress file from another run of the same plan is overwritten,
not appended to.

## Writing the file

The user watches the file live in the app's file pane, and that pane redraws
only when the file is changed through the file-editing tools. Change it with
**Edit** — one call per row or line that changes — and use **Write** only to
create it or rebuild it on a resumed run. Never write it from the shell
(`python`, `sed`, `cat >`, a heredoc, a script): the file on disk changes but
the pane keeps showing the old version until the user reopens it.

Change it the moment a status changes, not in a batch at the commit:
`🔄 в работе` when the unit is dispatched (with its executor), `🔍 на ревью`
when `code-review-unit` starts, `✅ закоммичен` right after the unit's commit
lands — and the progress bar line and the `Обновлено` time with each change. A
resumed run resets any in-between status from git (no `Plan-Unit:` trailer →
`⏳ ждёт`).

## The progress bar

Every progress view in the pipeline has the same shape: the title, then
right under it the bar alone in a ```` ```text ```` block, then the count on
its own line — «Сделано: N из M» for the plan, «Исправлено: N из M» for the
fixes section, «Проверено: N из M · успешно … · не прошли … · заблокировано … · не автоматизированы …» for the
user-test run, whose main bar shows the share of cases that pass — then the table:

````markdown
# Прогресс выполнения плана — итерация 1.1.0

```text
████████████████████████████████████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ 40%
```

Сделано: 8 из 20
````

The bar is a hundred cells, one per percent — `█` for done, `░` for the
rest — then the percent. The code block keeps it on one monospace line in
the file pane instead of wrapping into the prose around it. Every unit
weighs the same, whatever its grade or size: percent = ⌊done × 100 /
total⌋, rounded down so the bar never shows 100% before the last unit
lands, and the filled cells equal the percent. Done means `✅ закоммичен`
(units out of the run's scope do not count). The bar and the count change
in the same Edit as the row; the line under the table carries the run's
state and the update time. The fixes section has its own bar, in the same
shape, over its blocking findings (`✅ исправлено` of the rows that block).

## Fixes after the final review

When `code-review-full` returns anything but `PASS`, the fixes are planned in
the file **before the first fix is dispatched**, so the user can follow them
the same way as the units, and its link goes to the chat again before the
first fix (`work` → Step 7). Add this section under the units table, set the
`Финальное ревью:` line to the verdict:

````markdown
## Исправления по финальному ревью

```text
░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ 0%
```

Исправлено: 0 из 2

| F | Замечание | Важность | Юнит | Исполнитель | Статус | Ревью |
|---|---|---|---|---|---|---|
| F1 | лимит вместимости проверяется в сценарии, а не в сущности (BR-5) | P1 | U2 | impl-medium | ⏳ ждёт | — |
| F2 | старый валидатор вместимости остался в HTTP-адаптере | P1 | RF1 (U2, U5) | mechanical-worker | ⏳ ждёт | — |
| F3 | имя `roomCap` против `capacity` | P2 | — | — | 📝 в отчёт, не блокирует | — |

Вердикт: RETURN_TO_UNIT · замечаний 3 (P1 — 2, P2 — 1) · повторное ревью: ждёт · обновлено <YYYY-MM-DD HH:MM>
````

- **One row per finding**, in the review's order, with its severity. A
  blocking finding (P0/P1) names who fixes it: the unit it re-opens
  (`RETURN_TO_UNIT` — that unit's own implementer) or a follow-up `RF<n>` for
  a fix that spans units or a mechanical `FIX_THEN_CLOSE` item
  (`mechanical-worker`), with the units it touches in brackets; its commit
  trailer is `Plan-Unit: <version>/review-fix-<n>`. A P2/P3
  finding is `📝 в отчёт, не блокирует` and goes to the run report.
- **Statuses** as for units: `⏳ ждёт` → `🔧 исправляется` → `✅ исправлено`
  (commit sha in the Ревью cell after its `code-review-unit` verdict), or
  `⛔ остановлено: <причина>`.
- **The units table follows:** a re-opened unit's row reads
  `🔁 исправление F1` while it is open and `✅ исправлен (F1)` once its fix
  commit lands; a follow-up gets its own `RF<n>` row at the bottom of the
  units table.
- **Each fix updates its rows when its commit lands** (both tables, the
  section's bar and count, the update time), like a unit.
- **The re-review** (`code-review-full`, once, over the fix commits): its
  verdict goes to «повторное ревью:» on the line under the fixes table, and the `Финальное ревью:` line
  shows the path (`RETURN_TO_UNIT → исправлено → PASS`). A second blocking
  verdict is a stop: «Повторное ревью: <verdict> → остановлено, решает
  пользователь», its new findings listed under the same table as `F4`, `F5`…
  with `⛔ остановлено: ждёт решения`.
