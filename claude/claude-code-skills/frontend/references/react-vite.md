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
e2e/                       Playwright specs, one main path per S-n
```

Name the `S-n` in the page file's first comment line so a search for `S-1` finds it.

## Defaults — «по умолчанию, можно поменять»

| Concern | Default | Note |
|---|---|---|
| Routing | React Router; TanStack Router if already in the repo | one route per `S-n`, lazy-loaded |
| Server state | TanStack Query | query per read `operationId`, mutation per write; invalidate the list after a write |
| API client | openapi-typescript types + openapi-fetch | @hey-api/openapi-ts or Orval if the repo already uses one |
| Forms | React Hook Form + Zod via its resolver | schema typed against the generated request body |
| Styling / UI kit | Tailwind CSS + shadcn/ui | Radix-based primitives bring dialog focus trap and keyboard handling |
| Component tests | Vitest + Testing Library + jsdom, MSW at the network boundary | queries by role and accessible name |
| E2E / a11y | Playwright (`playwright-cli`); eslint-plugin-jsx-a11y | `@axe-core/playwright` scan of each state |

## Stack conventions

- No server of its own: the session is the API's cookie, so the client sends
  credentials and the app-wide handler owns `401`.
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

## Verify in current docs

- TanStack Query: query-key and invalidation API, option names and defaults
  (stale time, retries) in the installed major.
- Router: data-router vs component-router API, lazy routes, error elements.
- openapi-fetch / generator: CLI flags, output file, how non-2xx bodies and
  `response.status` are typed.
- Vite: which env variables reach client code and how they are typed; the
  test environment key in the Vitest config.
- React Hook Form resolver: support for the installed Zod major.
