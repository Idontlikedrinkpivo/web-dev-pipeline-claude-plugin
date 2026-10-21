# Vendored

Source: the playwright-cli skill, https://github.com/microsoft/playwright-cli, folder `skills/playwright-cli/`
(Apache License 2.0, `LICENSE` in this folder). The upstream commit was not recorded.

Adapted for this plugin:

- the description rewritten for the pipeline's skill listing;
- the `allowed-tools` line removed — the user's own permission settings decide which commands run;
- `work` gives a unit that writes Playwright specs or config only `references/test-config.md` and
  `references/playwright-tests.md` (`work/references/stack-skills.md`), not this SKILL.md.
