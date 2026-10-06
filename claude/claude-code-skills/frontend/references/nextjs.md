# Profile: Next.js (App Router)

For §1 «Стек» naming Next.js with the App Router (a Pages Router repo is "no
profile" — say so). The foundation §5 tree wins; this layout fills only what it leaves open.

## Layout

```
app/
  layout.tsx               root layout, providers mount point
  <route>/page.tsx         one route per S-n (Server Component by default)
  <route>/loading.tsx      the spec's Loading row when the read happens on the server
  <route>/error.tsx        the spec's Error row for a failed server read (client component)
features/<feature>/        api.ts (one function/hook per operationId), components, messages, *.test.tsx
shared/api/                generated types/client (never hand-edited) + client.ts
shared/ui/                 primitives — reuse before adding
e2e/                       Playwright specs, one main path per S-n
```

Name the `S-n` in the page file's first comment line.

## Defaults — «по умолчанию, можно поменять»

| Concern | Default | Note |
|---|---|---|
| Reads | Server Component calling the generated client, when the server can forward the session | otherwise a client component with TanStack Query |
| Writes | client component + TanStack Query mutation, or a Server Action | pick one per project and keep it |
| API client | openapi-typescript types + openapi-fetch | @hey-api/openapi-ts or Orval if already used |
| Forms | React Hook Form + Zod; Zod again in a Server Action | schema typed against the generated request body |
| Styling / UI kit | Tailwind CSS + shadcn/ui | |
| Component tests | Vitest + Testing Library + jsdom, MSW | async Server Components are covered by e2e instead |
| E2E | Playwright (`playwright-cli`), app started by `webServer` | `@axe-core/playwright` per state |

## Stack conventions

- The client/server boundary is a design decision per file: anything with
  state, effects, handlers or a modal is a client component (`"use client"`
  at the top), kept as a leaf; the page stays a server component when it can.
  Each such file carries the directive itself, even when today only a client
  parent imports it: a component that passes `onClick` or uses a hook without
  it works by accident and breaks the day a server component imports it.
- Modals, pending buttons and status messages are client-side even when the list
  is server-rendered; after a write, refresh the server data as the installed version prescribes.
- Server-only code (secrets, the internal backend URL) never imports into a client component.
- Hydration: an input with `value` has `onChange`, or uses `defaultValue`
  when uncontrolled; a date or time that differs between server and client
  (time zone, `Date.now()`) renders from a value the server passes or on
  the client after mount, so the HTML matches; `suppressHydrationWarning`
  only on the one element that must differ, never to silence a real
  mismatch (`web-design-guidelines` → Next.js hydration).

## Commands (read the real names from `package.json`)

| Purpose | Placeholder |
|---|---|
| dev / build | `<pm> run dev` / `<pm> run build` — build also catches server/client boundary errors |
| typecheck | `<pm> run typecheck` (or `tsc --noEmit`) |
| lint | `<pm> run lint` |
| test | `<pm> run test` / `<pm> exec playwright test` |
| API codegen | `<pm> run api:gen` — add it if missing |

## Verify in current docs

- Caching and revalidation defaults for `fetch` and route segments; refresh after a mutation.
- Route file conventions (loading, error, not-found), params typing, and
  navigation hooks in the installed major.
- Server Actions: form integration, returned errors, pending state hooks.
- Which env variables reach the browser; how rewrites/proxies to the API are configured.
- The generator's config and output; how its client runs on server and client.
