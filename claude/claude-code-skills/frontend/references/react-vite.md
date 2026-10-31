# Profile: React + Vite (SPA)

For §1 «Стек» naming React built with Vite, client-only. The architecture's
foundation §5 tree wins; this layout fills only what the tree leaves open.

## Layout

```
src/
  main.tsx                 entry: mounts <App/>, nothing else
  app/                     App, providers (query client, router), app-wide response handler
  pages/<screen>/          one folder per S-n; <Screen>Page.tsx composes features, states live here
  features/<feature>/      api.ts (one hook per operationId), components, modals, messages, *.test.tsx
  shared/api/              generated types/client (never hand-edited) + client.ts (base URL, credentials)
  shared/ui/               primitives (Button, Dialog, Toast) — reuse before adding
e2e/                       the user test suite — `ui-test-cases` owns it; screen units add no spec here
```

Name the `S-n` in the page file's first comment line so a search for `S-1` finds it.

## Defaults — «по умолчанию, можно поменять»

| Concern | Default | Note |
|---|---|---|
| Routing | React Router; TanStack Router if already in the repo | one route per `S-n`, lazy-loaded; declarative routes with TanStack Query as the one source of server data |
| Server state | TanStack Query | query per read `operationId`, mutation per write; invalidate the list after a write |
| API client | openapi-typescript types + openapi-fetch | @hey-api/openapi-ts or Orval if the repo already uses one |
| Forms | React Hook Form + Zod via its resolver | schema typed against the generated request body |
| Styling / UI kit | Tailwind CSS + shadcn/ui | Radix-based primitives bring dialog focus trap and keyboard handling |
| Component tests | Vitest + Testing Library + jsdom, MSW at the network boundary | queries by role and accessible name |
| E2E / a11y | Playwright, the user test suite of `ui-test-cases`; eslint-plugin-jsx-a11y | `@axe-core/playwright` scan of each state; whether jsx-a11y loads with the installed ESLint major — `version-checks.md` → «Profile: React + Vite» |

## Stack conventions

- No server of its own. The session travels as the architecture §1 decides: the API's `HttpOnly` cookie (the
  client sends credentials) or a Bearer token — the backend skills' default — kept in memory only, never in
  `localStorage` or `sessionStorage`. Either way the app-wide handler owns `401`.
- Loading/Error/Empty come from the query status of that screen, not a global
  spinner. Retry buttons call the query's refetch.
- The API base URL comes from a build-time env variable read in `shared/api/client.ts` only.

## Commands (read the real names from `package.json`)

| Purpose | Placeholder (`<pm>` = what the lockfile implies) |
|---|---|
| dev / build | `<pm> run dev` / `<pm> run build` |
| typecheck | `<pm> run typecheck` (or the `tsc` step inside `build`) |
| lint | `<pm> run lint` |
| test | `<pm> run test` / `<pm> exec playwright test` |
| API codegen | `<pm> run api:gen` — add it if missing |

Version-sensitive points of this profile: `version-checks.md` → «Profile: React + Vite».
