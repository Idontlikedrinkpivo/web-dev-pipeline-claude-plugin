# Playwright Test config essentials

Reuse the existing `playwright.config.ts`. When creating one for a new E2E unit:

```typescript
import { defineConfig, devices } from '@playwright/test'

export default defineConfig({
  testDir: './tests',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  use: { baseURL: process.env.BASE_URL ?? 'http://localhost:3000', trace: 'on-first-retry' },
  webServer: { command: 'npm run dev', url: 'http://localhost:3000', reuseExistingServer: !process.env.CI },
  projects: [
    { name: 'setup', testMatch: /.*\.setup\.ts/ },
    { name: 'chromium', use: { ...devices['Desktop Chrome'], storageState: 'playwright/.auth/user.json' }, dependencies: ['setup'] },
  ],
})
```

- Log in once in `tests/auth.setup.ts`, save `page.context().storageState({ path })`; add `playwright/.auth` to `.gitignore`. A setup project (rather than `globalSetup`) shows up in the HTML report, records traces, and can use fixtures.
- Navigate with relative paths (`page.goto('/')`) so `baseURL` controls the target.
- Web-first assertions only (`await expect(locator).toBeVisible()`); no `waitForTimeout`, no `networkidle`.

```typescript
// tests/auth.setup.ts
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
