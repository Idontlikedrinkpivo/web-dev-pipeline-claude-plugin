# What belongs in a unit's «Файлы»

Read when filling `Файлы` (Step 4) and by `plan-review`'s Files completeness lens.
`Файлы` is the unit's whole footprint: a file the executor must touch and the plan
did not list stops the unit (`BLOCKED`, or a scope breach the review flags) and
costs a round. Runs measured this: 11 and 7 corrections of `Файлы` in two runs of
one project, each a stop. Most came from the five cases below.

1. **The unit's own files** — the code it writes or changes, and the test file of
   each behaviour it adds.
2. **New test files the evidence strategy needs.** A unit with
   `characterization-first`, a two-phase unit, or a split «без изменения
   поведения» that pins behaviour in a new file lists that file — when the plan's
   §1 says new checks go into new test files, each unit names its new file here.
3. **Everything that uses what the unit removes or renames.** A deleted file, a
   removed export, a renamed component: the unit lists it in «Меняет символы», and
   every hit of a repository search (code, tests, e2e, fixtures, CI, the dead-code
   tool's config) is in `Файлы` or under «Не затрагивается» with its reason. The
   dead-code check (`knip`, `vulture`) fails on a consumer left behind.
4. **Files an earlier unit splits, moves or renames.** When unit K splits, moves or
   renames a file, every later unit whose `Файлы` names the old path gets the new
   paths — or, when K decides them, the line `<old path> → по итогам U<K>`. A
   helper or a structural test K creates and later units use is in their `Файлы`
   too.
5. **Configs of a tool or a dependency the unit changes.** A unit that changes a
   dependency's major version, or a tool (the test runner, the linter, the bundler),
   lists the configs that read or resolve it: `vite.config.*`, `vitest.config.*`,
   `.dependency-cruiser.*`, `knip.*`, `eslint.config.*`, `tsconfig*.json`,
   `pyproject.toml` sections. A major upgrade that changes a type (React's
   `RefObject<T | null>`) lists the files the typecheck will name — run it on a
   scratch branch, or search for the changed type, before writing the unit.

A unit that leaves part of its work to a later one («отложено до U<N>») names those
sites in U<N>'s `Файлы` in the plan, not only in its own report.

During the run, `work` corrects a later unit's `Файлы` from what earlier units did
(`work/references/run-hygiene.md` → Files the plan did not list) — this file is
what keeps that list short.
