# playwright-cli and Playwright Test — version-sensitive points

Facts that change between releases. The skill deliberately gives no answer here, because the answer depends on the
installed version: read it from the lockfile or manifest (or `playwright-cli --version`), then check the point —
`work` does it once per run through Context7 (`work/references/context7.md`) and pastes the answers into the
packet's `CURRENT LIB DOCS`; elsewhere, Context7 (`resolve-library-id`, then `query-docs`) or a quick probe in the
project.

- **Which binary you are driving and its command set.** The global `playwright-cli` (`@playwright/cli`) and the project's `npx playwright cli` ship different command lists and flags. Before using a command from this skill, confirm it in `playwright-cli --help` / `--help <command>`: an unknown command or flag fails, and a renamed one sends you to the wrong output.
- **Where generated files land.** Snapshots, traces, videos, and auto-named screenshots or state files go to a default output folder; check where, and that it is gitignored before committing.
- **Session daemon lifetime.** Idle timeout, what `close` / `delete-data` remove, and where a persistent profile lives.
- **`gh --attach`.** The minimum `gh` version on the machine or runner, which token types the upload accepts, which GitHub hosts support it, and current size limits.
- **Playwright Test options.** That each `use`, `webServer`, and `projects` key you write exists in the installed `@playwright/test`, where `test-results` / report artifacts land, and what the test-agent init command generates (plan / generate / heal).
- **Video overlay APIs.** That `page.screencast` and its chapter / overlay methods exist in the installed Playwright before building a hero script on them.
