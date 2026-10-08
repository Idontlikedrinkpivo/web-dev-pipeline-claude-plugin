# The iteration summary

Read at the end of the pipeline, or when the user asks «итог», «сводка».

`documentation/plans/<version>/summary.md`, beside the plan — one
iteration, one page, so the user judges the pipeline by numbers rather
than by impression, and sees which stage to fix when something slipped.
The session writes it from the reports already on disk; it reads no code
and dispatches nothing. A report that is missing gives a `—` cell with the
reason (stage skipped, gate skipped), never a guess.

```markdown
# Итог итерации — <version>

| Этап | Показатель | Значение | Источник |
|---|---|---|---|
| Документы | противоречий найдено до плана | 4 (P0 2, P1 2) → исправлено | docs-consistency.md |
| План | грейд · вердикт plan-review с первого раза · доработок | Mid · FIX_THEN_PROCEED · 1 (plan-lite) | plan-review.md |
| Код | юнитов · вернулось на переделку · эскалаций · исправлений грейда | 12 · 2 · 1 · 1 | run report (`.git/pipeline-work/<version>-run.md`) |
| Ревью | находок P0/P1 по юнитам · вердикт финального ревью | 3 · PASS | run report, Full-plan review |
| UI-тесты | кейсов · прошли с первого прогона · дефектов пережило ревью | 22 · 19 · 2 | test-run.md |
| Безопасность | вердикт · P0/P1 найдено → исправлено · риск принят | FIX → PASS · 0/2 → 2 · 0 | security-audit.md |
| Гейты | пропущены | grill-me (S-13, маленькая правка) | отчёты этапов |
| Цена | токены / деньги / время, если сессия их показывает | — | статистика сессии |

## Проскочившие дефекты
Заполняет пользователь, когда находит дефект после «готово».
| Дефект | Где нашли | Какой этап должен был поймать |
|---|---|---|

## Ручные вмешательства
| Что поправили руками | Документ / план / код | Почему пайплайн не справился |
|---|---|---|
```

Below the table, one line naming the weakest stage of this iteration (the
most returns, defects, or interventions), or «слабых мест не видно». The
two lower tables start empty; the user fills them later. Escaped defects
are the main measure of the pipeline: each one names the stage whose skill
needs a fix.
