# Vendored

Source: the playwright-cli skill, https://github.com/microsoft/playwright-cli, folder `skills/playwright-cli/`
(Apache License 2.0, `LICENSE` in this folder), upstream commit `8eebb9a` (2026-09-14, «chore: roll Playwright to
1.64.0-alpha-2026-09-14»). The commit was not written down when the copy was taken; it was identified on 2026-10-22
as the last upstream commit touching that folder whose reference files match this copy outside the changes below
(`tracing.md`, `session-management.md`, `request-mocking.md`, `playwright-tests.md` identical; the next commit,
`5bd70cd`, rewrote `video-recording.md`).

Adapted for this plugin:

- the description rewritten for the pipeline's skill listing;
- the `allowed-tools` line removed — the user's own permission settings decide which commands run;
- `work` gives a unit that writes Playwright specs or config only `references/test-config.md` and
  `references/playwright-tests.md` (`work/references/stack-skills.md`), not this SKILL.md;
- `SKILL.md` — the working loop, the version-sensitive checklist (its points in `references/version-checks.md`, a
  file of this plugin, so `work` can check them through Context7), the interactive session limited to a person in
  the conversation; the global install of `@playwright/cli` asks the user first;
- `references/test-config.md` — the config written for the pipeline's parallel stands: `testDir: './e2e'`, one
  worker, `fullyParallel: false`, the address from `E2E_BASE_URL`, no `webServer`;
- `references/test-generation.md` — the «Inside dev-pipeline» block (only §0 and §3.1–3.3 apply to an agent working
  from reviewed documents); relative `page.goto`; generation one scenario at a time; healing never touches app code;
- `references/storage-state.md`, `references/running-code.md` — state files kept under the gitignored
  `playwright/.auth/`;
- `references/video-recording.md` — `gh --attach` without a pinned minimum version.

Updating: diff the upstream folder from `8eebb9a` to the new commit, apply what changed, keep the adaptations above,
and write the new commit here and in `THIRD_PARTY_NOTICES.md`.
