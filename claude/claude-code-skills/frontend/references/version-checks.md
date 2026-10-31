# Frontend — version-sensitive points

Facts that change between releases. Each point is a question for the installed version (read it from the
lockfile); an answer written beside a point is a dated hint, so confirm it against that version before relying on it.
`work` asks once per run (`work/references/context7.md`); elsewhere, Context7 or a quick probe in the project.

- **Rendering and data fetching** — where data loads (server, client, both), what is cached, for how long, and how
  to invalidate after a mutation.
- **Router APIs** — file conventions, params, navigation calls, loading/error boundaries, redirects.
- **Forms and validation** — how the form library binds a schema, and whether the schema library's installed major
  is the one its resolver supports.
- **OpenAPI client generator** — config file name and keys, output path, client flavour, how errors and non-2xx
  statuses are typed.
- **React major** — whether the installed React takes `ref` as an ordinary prop (no `forwardRef`) and renders
  `<Context>` as its own provider (both from React 19).
- **UI kit defaults** — whether the installed shadcn/ui version's stock theme passes contrast: its light
  `destructive` variant and its neutral `outline` and input borders against their backgrounds (4.5:1 for text, 3:1
  for boundaries; earlier versions fell below it). A failing pair is fixed in the project's theme (`SKILL.md` →
  Accessibility baseline).

Of the two profile sections below, ask only the one the architecture's §1 «Стек» names (`SKILL.md` → Pick the stack
profile).

## Profile: Next.js (`nextjs.md`)

- Caching and revalidation defaults for `fetch` and route segments; refresh after a mutation.
- Route file conventions (loading, error, not-found), params typing, and
  navigation hooks in the installed major.
- Server Actions: form integration, returned errors, pending state hooks.
- Which env variables reach the browser; how rewrites/proxies to the API are configured.
- The generator's config and output; how its client runs on server and client.

## Profile: React + Vite (`react-vite.md`)

- TanStack Query: query-key and invalidation API, option names and defaults
  (stale time, retries) in the installed major.
- Router: data-router vs component-router API, lazy routes, error elements;
  which package the installed React Router major is imported from
  (`react-router-dom` was folded into `react-router` in a recent major) and
  the React version it requires.
- openapi-fetch / generator: CLI flags, output file, how non-2xx bodies and
  `response.status` are typed.
- Vite: which env variables reach client code and how they are typed; the
  test environment key in the Vitest config.
- React Hook Form resolver: support for the installed Zod major.
- eslint-plugin-jsx-a11y: that it loads with the installed ESLint major — it
  has lagged ESLint releases; if it does not, say so in the report rather
  than pinning ESLint back.
