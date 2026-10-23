# Playwright Test config essentials

Reuse the existing `playwright.config.ts`. When creating one for a new E2E suite, write it ready for the pipeline's
parallel stands (`ui-test-cases` → `references/parallel-stands.md`): tests on one stand share its database and
users, so a stand gets one worker; speed comes from more stands, each running its own share of the files at its own
address.

```typescript
import { defineConfig, devices } from '@playwright/test'

export default defineConfig({
  testDir: './e2e',                // the project's E2E folder; the user test suite lives here (ui-test-cases)
  fullyParallel: false,            // tests in one file may build on each other's data
  workers: 1,                      // one worker per stand: two on one database break each other's counts
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  use: {
    baseURL: process.env.E2E_BASE_URL ?? 'http://localhost:3000', // each stand passes its own address
    trace: 'on-first-retry',
  },
  // No webServer: the stand (database, API, front) is started by the project's verify skill or
  // scripts/e2e-stands.sh, each copy on its own ports; a webServer here would start a second app on a fixed port.
  projects: [
    { name: 'setup', testMatch: /.*\.setup\.ts/ },
    { name: 'chromium', use: { ...devices['Desktop Chrome'], storageState: 'playwright/.auth/user.json' }, dependencies: ['setup'] },
  ],
})
```

- The default address is today's local one; a stand passes `E2E_BASE_URL` (and `E2E_API_URL` when a test seeds through
  the API), never an edited config. A project whose config already reads another variable keeps it and names it in
  the verify skill.
- Log in once in `e2e/auth.setup.ts`, save `page.context().storageState({ path })`; add `playwright/.auth` to `.gitignore`. A setup project (rather than `globalSetup`) shows up in the HTML report, records traces, and can use fixtures. Several roles: one setup test and one state file per role (`playwright/.auth/<role>.json`).
- Navigate with relative paths (`page.goto('/')`) so `baseURL` controls the target.
- Web-first assertions only (`await expect(locator).toBeVisible()`); no `waitForTimeout`, no `networkidle`.
- In CI the suite is split by shards (`--shard=<i>/<N>`), each shard with its own stand — the same one-worker rule
  (`ui-test-cases` → `references/parallel-stands.md` → In CI).

```typescript
// e2e/auth.setup.ts
import { test as setup, expect } from '@playwright/test'

const authFile = 'playwright/.auth/user.json'

setup('authenticate', async ({ page }) => {
  await page.goto('/login')
  await page.getByLabel('Email').fill(process.env.E2E_USER!)
  await page.getByLabel('Password').fill(process.env.E2E_PASSWORD!)
  await page.getByRole('button', { name: 'Sign in' }).click()
  await expect(page.getByRole('button', { name: 'Account' })).toBeVisible()
  await page.context().storageState({ path: authFile })
})
```
