---
name: playwright-cli
description: >-
  Drives a real browser from the shell with playwright-cli — snapshots,
  clicks by element ref, request mocks, sessions, traces and video — and
  runs Playwright Test end to end: config, debugging, and generating tests
  through plan, generate, heal. Use when a task needs to check or reproduce
  web UI behaviour, write or fix E2E tests, set up playwright.config, or
  attach screenshots to a PR. Not for unit or API tests without a browser
  (Vitest, pytest) or fetching a page that needs no interaction.
allowed-tools: Bash(playwright-cli:*) Bash(npx playwright:*) Bash(npx @playwright/cli:*)
---

# Browser Automation with playwright-cli

## Working loop

Every browser task is the same loop: snapshot → ref → action → verify, repeated, then close.

1. **Open.** `playwright-cli open <url>`. The browser lives in a background daemon between commands, so each later command acts on the same page.
2. **Snapshot.** Read the snapshot the last command returned (the `[Snapshot](...)` file), or run `playwright-cli snapshot`. It is the page as a text accessibility tree with refs (`e15`): cheaper than a screenshot and where refs come from. On a large page run `find "<text>"` (if your build has it, see Version-sensitive behaviour), or `snapshot --depth=4` and then `snapshot <ref>`, instead of reading the whole tree (see Snapshots).
3. **Ref.** Take the target's ref from the newest snapshot. A ref belongs to the snapshot it came from; after a navigation or re-render it may point at nothing or at another element.
4. **Action.** Run one command per action (`fill e5 "..."`, `click e7`, `press Enter`), so the snapshot it returns shows the effect of that action alone.
5. **Verify.** Check the expected change in the returned snapshot: URL, heading, message, field value. Use `find` or `eval` when it is not visible there. A command that exits cleanly only proves the event fired, not that the app reacted. If the check fails, read `console` and `requests` before retrying (see Example: Debugging with DevTools). If it passes, go back to step 2 for the next action.
6. **Close.** Run `playwright-cli close` (or `-s=<name> close`) when the task is done. Otherwise the daemon keeps the browser, its cookies, and the page alive, and the next task starts in that stale state.

Take a screenshot only when a human needs the picture (a PR, a bug report). It gives no refs and costs more to read than a snapshot.

Example — log in and confirm the dashboard:

```bash
playwright-cli open https://app.example.com/login
# snapshot: textbox "Email" [ref=e12], textbox "Password" [ref=e14], button "Sign in" [ref=e16]
playwright-cli fill e12 "qa@example.com"
playwright-cli fill e14 "correct-horse-battery"
playwright-cli click e16
# returned snapshot: Page URL https://app.example.com/dashboard, heading "Welcome, QA"
playwright-cli find "Welcome, QA"
playwright-cli close
```

## Commands

### Core

```bash
playwright-cli open
# open and navigate right away
playwright-cli open https://example.com/
playwright-cli goto https://playwright.dev
playwright-cli type "search query"
playwright-cli click e3
playwright-cli dblclick e7
# --submit presses Enter after filling the element
playwright-cli fill e5 "user@example.com"  --submit
playwright-cli drag e2 e8
# drop files or data onto an element (from outside the page)
playwright-cli drop e4 --path=./image.png
playwright-cli drop e4 --data="text/plain=hello world"
playwright-cli hover e4
playwright-cli select e9 "option-value"
playwright-cli upload ./document.pdf
playwright-cli check e12
playwright-cli uncheck e12
playwright-cli snapshot
# search the snapshot instead of reading it all - see Snapshots below
# (depends on the installed playwright-cli version - check --help)
playwright-cli find "Sign in"
playwright-cli eval "document.title"
playwright-cli eval "el => el.textContent" e5
# get element id, class, or any attribute not visible in the snapshot
playwright-cli eval "el => el.id" e5
playwright-cli eval "el => el.getAttribute('data-testid')" e5
playwright-cli dialog-accept
playwright-cli dialog-accept "confirmation text"
playwright-cli dialog-dismiss
playwright-cli resize 1920 1080
playwright-cli close
```

### Navigation

```bash
playwright-cli go-back
playwright-cli go-forward
playwright-cli reload
```

### Keyboard

```bash
playwright-cli press Enter
playwright-cli press ArrowDown
playwright-cli keydown Shift
playwright-cli keyup Shift
```

### Save as

```bash
playwright-cli screenshot
playwright-cli screenshot e5
playwright-cli screenshot --filename=page.png
playwright-cli screenshot --hires
playwright-cli pdf --filename=page.pdf
```

### Tabs

```bash
playwright-cli tab-list
playwright-cli tab-new
playwright-cli tab-new https://example.com/page
playwright-cli tab-close
playwright-cli tab-close 2
playwright-cli tab-select 0
```

### Storage

```bash
# save a logged-in state once, load it instead of logging in again;
# keep state files under playwright/.auth/ and gitignore that folder (session cookies)
mkdir -p playwright/.auth
playwright-cli state-save playwright/.auth/user.json
playwright-cli state-load playwright/.auth/user.json
```

Cookies (`cookie-list/get/set/delete/clear`), `localstorage-*` and `sessionstorage-*`: read [references/storage-state.md](references/storage-state.md) when a task reads or seeds cookies or web storage.

### Mouse, WebMCP, open parameters

Read [references/more-commands.md](references/more-commands.md) when:
- a ref or locator cannot target the element and you need raw `mousemove` / `mousedown` / `mousewheel`;
- you need a specific browser, mobile emulation (`open --mobile` gives smaller, cheaper snapshots; depends on the installed playwright-cli version — check `--help`), a persistent profile, a config file, or to `attach` to an already running browser;
- the page status says `N webmcp tools available on the page` — one page-provided tool call may replace a sequence of clicks (`webmcp-*` commands depend on the installed playwright-cli version — check `--help`).

### Network

```bash
playwright-cli route "**/*.jpg" --status=404
playwright-cli route "https://api.example.com/**" --body='{"mock": true}'
playwright-cli route-list
playwright-cli unroute "**/*.jpg"
playwright-cli unroute
```

### DevTools

```bash
playwright-cli console
playwright-cli console warning
playwright-cli requests
playwright-cli request 5
playwright-cli run-code "async page => await page.context().grantPermissions(['geolocation'])"
playwright-cli run-code --filename=script.js
playwright-cli tracing-start
playwright-cli tracing-stop

# record user actions in the browser, print them as Playwright code on stop
playwright-cli recording-start
playwright-cli recording-stop

playwright-cli video-start video.webm
playwright-cli video-chapter "Chapter Title" --description="Details" --duration=2000
playwright-cli video-stop

# annotate each subsequent action (click, type, ...) with a callout naming the action and highlighting the target
# (depends on the installed playwright-cli version - check --help)
playwright-cli video-show-actions --duration=600 --position=top-right
playwright-cli video-hide-actions

# launch the dashboard for UI review / design feedback — user annotates the page, you receive the annotated screenshot, snapshot, and notes
playwright-cli show --annotate

# generate a Playwright locator for an element from its ref or selector
playwright-cli generate-locator e5 --raw

# show a persistent highlight overlay for an element, optionally with a custom style
playwright-cli highlight e5
playwright-cli highlight e5 --style="outline: 3px dashed red"
# hide a single element highlight, or all page highlights when no target is given
playwright-cli highlight e5 --hide
playwright-cli highlight --hide
```

## Raw output

The global `--raw` option strips page status, generated code, and snapshot sections from the output, returning only the result value. Use it to pipe command output into other tools. Commands that don't produce output return nothing.

```bash
playwright-cli --raw eval "JSON.stringify(performance.timing)" | jq '.loadEventEnd - .navigationStart'
playwright-cli --raw eval "JSON.stringify([...document.querySelectorAll('a')].map(a => a.href))" > links.json
playwright-cli --raw snapshot > before.yml
playwright-cli click e5
playwright-cli --raw snapshot > after.yml
diff before.yml after.yml
TOKEN=$(playwright-cli --raw cookie-get session_id)
playwright-cli --raw localstorage-get theme
```

For structured output wrapping every reply as JSON, pass --json
```bash
playwright-cli list --json
```

## URLs with `&` on Windows

On Windows, `cmd.exe` and PowerShell treat `&` as a command separator, so URLs with multiple query parameters get truncated before `playwright-cli` runs. Escape `&` with `^&` in `cmd.exe`, or use `--%` in PowerShell:

```batch
playwright-cli goto "https://example.com/?a=1^&b=2"
```

```powershell
playwright-cli --% goto "https://example.com/?a=1&b=2"
```

## Snapshots

After each command, playwright-cli provides a snapshot of the current browser state.

```bash
> playwright-cli goto https://example.com
### Page
- Page URL: https://example.com/
- Page Title: Example Domain
### Snapshot
[Snapshot](.playwright-cli/page-2026-02-14T19-22-42-679Z.yml)
```

You can also take a snapshot on demand using `playwright-cli snapshot` command. All the options below can be combined as needed.

```bash
# default - save to a file with timestamp-based name
playwright-cli snapshot

# save to file, use when snapshot is a part of the workflow result
playwright-cli snapshot --filename=after-click.yaml

# snapshot an element instead of the whole page
playwright-cli snapshot "#main"

# limit snapshot depth for efficiency, take a partial snapshot afterwards
playwright-cli snapshot --depth=4
playwright-cli snapshot e34

# include each element's bounding box as [box=x,y,width,height]
playwright-cli snapshot --boxes

# search a large snapshot instead of capturing it all — returns matching nodes
# (depends on the installed playwright-cli version - check --help)
# with 3 lines of context around each match (like grep -C)
playwright-cli find "Add to cart"
playwright-cli find --regex "\\$[0-9]+\\.[0-9]{2}"
# wrap the regexp in slashes to add flags, e.g. /i for case-insensitive
playwright-cli find --regex "/sign (in|up)/i"
```

## Targeting elements

By default, target elements by ref (Working loop, step 3). Use a CSS selector or a Playwright locator when you hit the same element again after page loads: it re-resolves each time, while a ref needs a fresh snapshot.

```bash
# css selector
playwright-cli click "#main > button.submit"

# role locator
playwright-cli click "getByRole('button', { name: 'Submit' })"

# test id
playwright-cli click "getByTestId('submit-button')"
```

## Browser Sessions

A named session (`-s=<name>`) keeps its own browser, cookies, and storage, so parallel flows (two users, a scraper beside a test) do not share state. Use `kill-all` only when `close` hangs or `list` shows browsers you did not open, because it kills every daemon, including other agents' sessions.

```bash
# create new browser session named "mysession" with persistent profile
playwright-cli -s=mysession open example.com --persistent
# same with manually specified profile directory (use when requested explicitly)
playwright-cli -s=mysession open example.com --profile=/path/to/profile
playwright-cli -s=mysession click e6
playwright-cli -s=mysession close  # stop a named browser
playwright-cli -s=mysession delete-data  # delete user data for persistent session

playwright-cli list
# Close all browsers
playwright-cli close-all
# Forcefully kill all browser processes
playwright-cli kill-all
```

## Installation

If global `playwright-cli` command is not available, try a local version via `npx playwright cli`:

```bash
npx --no-install playwright --version
```

The local `npx playwright cli` may lack commands this skill uses (`drop`, `highlight`, `generate-locator`, recording, `requests`). Check `npx playwright cli --help` for the command you need: use the local one when it has it — it matches the project's Playwright version and installed browsers — otherwise the global `playwright-cli`. When neither is installed, install the global command:

```bash
npm install -g @playwright/cli@latest
```

## Version-sensitive behaviour

This skill does not pin library facts that change between releases (signatures, defaults, generated-artifact paths, "since version X"). Before relying on one: read the installed version from the lockfile or manifest, then check current docs via the context7 MCP (`resolve-library-id`, then `query-docs`) or run a quick probe in the project. The checklist below names where the silent pitfalls usually are; it deliberately does not give the answer, because the answer depends on the version.

### Check before relying on it

- **Which binary you are driving and its command set.** The global `playwright-cli` (`@playwright/cli`) and the project's `npx playwright cli` ship different command lists and flags. Before using a command from this skill, confirm it in `playwright-cli --help` / `--help <command>`: an unknown command or flag fails, and a renamed one sends you to the wrong output.
- **Where generated files land.** Snapshots, traces, videos, and auto-named screenshots or state files go to a default output folder; check where, and that it is gitignored before committing.
- **Session daemon lifetime.** Idle timeout, what `close` / `delete-data` remove, and where a persistent profile lives.
- **`gh --attach`.** The minimum `gh` version on the machine or runner, which token types the upload accepts, which GitHub hosts support it, and current size limits.
- **Playwright Test options.** That each `use`, `webServer`, and `projects` key you write exists in the installed `@playwright/test`, where `test-results` / report artifacts land, and what the test-agent init command generates (plan / generate / heal).
- **Video overlay APIs.** That `page.screencast` and its chapter / overlay methods exist in the installed Playwright before building a hero script on them.

## Example: Debugging with DevTools

Reproduce the failing steps, then read `console` and `requests` before guessing; wrap the steps in `tracing-start` / `tracing-stop` when you need DOM and network history (read [references/tracing.md](references/tracing.md)).

```bash
playwright-cli open https://example.com
playwright-cli click e4
playwright-cli fill e7 "test"
playwright-cli console
playwright-cli requests
playwright-cli close
```

## Example: Interactive session

Ask the user for UI review or design feedback. The user draws boxes on the live page and types comments; you receive the annotated screenshot, the snapshot of the marked region, and the user's notes. Use this only when a person is in the conversation and asked for "UI review", "design feedback", or what they think. Never from a subagent or a headless run (`impl-ui` in `work`, a benchmark run): nobody is there to annotate, and the command waits forever — report the question in the final answer instead.

```bash
playwright-cli open https://example.com
playwright-cli show --annotate
```

## Attaching screenshots and videos to pull requests

A recent `gh` uploads local images and videos with the repeatable `--attach` flag (check `gh pr comment --help` for `--attach` before relying on it) on `gh pr create`, `gh pr comment` and `gh issue comment`. Attach a screenshot or a short video when it saves the reviewer a checkout: a UI fix, a before/after pair, a new user-facing flow, or the failure state in a bug report.

```bash
playwright-cli screenshot --filename=settings-after.png
gh pr comment 123 --body "Settings page after the fix." --attach ./settings-after.png
```

See [references/pr-attachments.md](references/pr-attachments.md) for alt text, inline references, size limits and attaching test artifacts from CI (the upload rejects the workflow's `GITHUB_TOKEN`; CI needs a fine-grained PAT stored as a secret).

## Specific tasks

Read the reference only when the task matches its trigger:

* **Playwright Test config, baseURL, webServer, auth setup project** [references/test-config.md](references/test-config.md) — read when creating or changing `playwright.config.ts`, or when tests need a running dev server or a logged-in state.
* **Running and Debugging Playwright tests** [references/playwright-tests.md](references/playwright-tests.md) — read before running `npx playwright test` or when a spec fails and you need to debug it.
* **Request mocking** [references/request-mocking.md](references/request-mocking.md) — read when a flow depends on a backend response you must fake, delay, or block beyond a single `route`.
* **Running Playwright code** [references/running-code.md](references/running-code.md) — read when no CLI command covers the action (permissions, geolocation, waiting on events) and you need `run-code`.
* **Browser session management** [references/session-management.md](references/session-management.md) — read when running several browsers at once, reusing a named session, or attaching to a running browser.
* **Storage state (cookies, localStorage)** [references/storage-state.md](references/storage-state.md) — read when reading, seeding, or clearing cookies, localStorage, or sessionStorage, or saving auth state.
* **Test generation (plan / generate / heal)** [references/test-generation.md](references/test-generation.md) — read when asked to write new E2E specs from a scenario or to repair failing E2E tests. Repairing touches tests and specs, never app code: when the app itself looks wrong, stop and ask whether it is a regression.
* **Tracing** [references/tracing.md](references/tracing.md) — read when a failure needs the DOM, network, and console history of every step.
* **Video recording** [references/video-recording.md](references/video-recording.md) — read when the deliverable is a video: a demo, a bug reproduction, or a PR walkthrough.
* **Attaching screenshots and videos to pull requests** [references/pr-attachments.md](references/pr-attachments.md) — read before attaching artifacts with `gh --attach` (see the section above).
* **Inspecting element attributes** [references/element-attributes.md](references/element-attributes.md) — read when the snapshot lacks an `id`, `class`, `data-*`, or other DOM property you need.
* **Mouse, open parameters, WebMCP** [references/more-commands.md](references/more-commands.md) — read in the cases listed under Commands → "Mouse, WebMCP, open parameters".
