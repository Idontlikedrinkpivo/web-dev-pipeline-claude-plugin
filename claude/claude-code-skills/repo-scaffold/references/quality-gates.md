# Quality gates

The checks every project carries from its first commit, and that `work` runs after every unit and `ci-pipeline`
runs on every push. They exist because an agent writes code fast and drifts in predictable ways — functions that
grow past understanding, copied blocks, swallowed errors, pages that become monoliths, tests nobody type-checks.
A deterministic gate catches these at once and for free; a reviewer catches them late, if at all. Rules a machine
can check are gates, not prose in a prompt.

## The gates — every part of the repository (backend, frontend, each service)

| Gate | What it refuses | Why |
|---|---|---|
| Code linter | the rules below | the cheapest check; the agent sees the error and fixes it in the same unit |
| Types, tests included | a type error anywhere, test files too | tests that drift from the code stop telling what broke |
| Boundaries | an import across a layer, for the frontend too | the architecture's layers hold only while a machine checks them |
| Dead code | an unused file, export or dependency | leftovers of a rewrite hide the live path |
| Duplicates | duplication above the threshold | an agent copies sooner than it reuses; copies drift |
| Test hygiene | a committed `.only` / `.skip` / `todo`; a test reading a `.css` or source file | a skipped test is a silent hole; a test of the stylesheet breaks on harmless edits |
| Dependency audit | a high or critical vulnerability in a production dependency (development tools — a warning) | a known hole shipped with the release |

### Linter rules and thresholds

| Rule | Threshold | The message says how to fix |
|---|---|---|
| cyclomatic complexity per function | 15 | «вынеси ветки в именованные функции или в метод сущности» |
| function length | 80 lines in production code | «раздели на шаги; у компонента — данные в хук, вид отдельно» |
| file length | 500 lines in production code, 800 in a test file | «раздели по ответственности; тесты — по поведению, общее — в помощники» |
| nesting depth | 4 | «ранний выход вместо вложенного if» |
| parameters | 5 | «объект параметров» |
| empty `catch` / bare `except` / `except: pass` | forbidden | «запиши причину в лог или верни именованную ошибку» |
| a promise nobody awaits | forbidden | «await или явный void с причиной» |
| a `switch` over a union that misses a case | forbidden | «добавь ветку — новая ошибка или статус не должны уходить молча» |
| React hooks rules | on, for a React frontend | — |

The numbers are the defaults; foundation §6 may tighten them, never loosen them without a reason in a row.

### By stack

- **TypeScript (backend and frontend):** ESLint flat config with `typescript-eslint` `recommended-type-checked`
  as the base (type-aware, `projectService`) plus `no-floating-promises`, `no-misused-promises`,
  `switch-exhaustiveness-check`, `only-throw-error`, `prefer-promise-reject-errors`, `no-unsafe-type-assertion`,
  `use-unknown-in-catch-callback-variable` (both outside `recommended-type-checked`), `no-non-null-assertion`,
  `return-await` (`in-try-catch`), `no-unnecessary-condition`; core `preserve-caught-error` (ESLint 9.35 or later)
  with `requireCatchParameter: true` and `errorClassNames` listing the project's own error classes (by default it
  checks only the built-in `Error` types);
  `no-restricted-syntax` against an empty error subclass and an empty `catch` block; on the frontend
  `no-restricted-syntax` against a regex literal in components and `no-restricted-imports` / `no-restricted-globals`
  keeping `fetch` and the API client inside the data layer; `@eslint-community/eslint-comments`
  (`require-description`, `no-unlimited-disable`) so a rule is never silenced without a reason; the rule set the
  `typescript` and `react` skills name; core `complexity`, `max-lines`, `max-lines-per-function`,
  `max-depth`, `max-params`, `no-empty`; `eslint-plugin-react-hooks` v7 with its `recommended` config on a React
  frontend (it carries the compiler rules: purity, refs, set-state-in-effect, static components), with
  `@eslint-react/eslint-plugin` for `@eslint-react/no-array-index-key`;
  `eslint-plugin-testing-library` and `@vitest/eslint-plugin` (focused and disabled tests, tests without an
  assertion) for the tests; a `tsconfig` for tests (or
  tests in the main one) so `typecheck` covers them; `dependency-cruiser` per part; `knip` per part; `jscpd` with
  `--threshold` (3 for production code, 8 for tests). The TypeScript major is a decision, not `latest`: pin the
  newest one `typescript-eslint` supports in its peer range (TypeScript 7 is not yet in it as of 2026-10), and
  record it in foundation §1 «Стек».
- **Python:** Ruff with `C901` (max-complexity 15), `PLR0912`, `PLR0913`, `PLR0915`, `E722`, `BLE001`, `S110`, `B`
  (including `B904`, `raise … from`), `TRY`, `ASYNC`, `RUF006`, `FAST`, `PT`, `DTZ`, `UP`; `mypy --strict` or pyright
  `strict` over `src` and `tests/` (ty only beside them while it is in beta); `import-linter`; `vulture`; `jscpd`; pytest without committed `skip` marks except with a
  reason.
- **Other stacks:** the linter the stack file names, configured to the same table.

## Tests that prove something

- **Property tests** — `fast-check` (TypeScript) or `hypothesis` (Python) installed from the start; the plan gives an
  invariant over many values a property scenario.
- **Mutation testing** — Stryker (TypeScript, incremental mode) or `mutmut` (Python) installed; `work` runs it only
  on the files of units that enforce an invariant row or are graded High, and once at the run's close over the
  run's diff. A surviving mutant is a review finding, not a hard threshold — mutation runs are slow, so they stay
  narrow.

## A project that already has code — the ratchet

Turning every threshold into an error on an old codebase stops all work at once. Instead:

1. Measure once and write the offenders into the linter config as a named legacy list: the files over a threshold get
   that rule as a warning; every other file gets it as an error.
2. A file leaves the list when it is fixed; the list never grows — a new or changed file meets the full rules.
3. The duplicate threshold starts at today's figure and only goes down.
4. Type errors in tests are fixed, not listed — they are real defects.

## Where the gates run

- `lint` runs the linter, boundaries, dead code and duplicates; `typecheck` covers tests; `test` runs the suite —
  the same three commands in every part (`repo-scaffold`).
- `work` runs `lint` and `typecheck` after every unit, before the review; an error in the unit's files is a return.
- `ci-pipeline` runs the three commands for every part; a part without one of them is a stop, not a pass. The
  dependency audit runs in its advisory `security` job (production dependencies at high and critical fail that
  job, the rest warn) until the team makes it required.
- At a run's close `work` measures duplicates, the longest and most complex functions and files against the run's
  base, and a simplifier pass removes what grew without changing behaviour (`work/references/health.md`).
