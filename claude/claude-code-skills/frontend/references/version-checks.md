# Frontend — version-sensitive points

Facts that change between releases. The skill deliberately gives no answer here, because the answer depends on the
installed version: read it from the lockfile, then check the point — `work` does it once per run through Context7
(`work/references/context7.md`) and pastes the answers into the packet's `CURRENT LIB DOCS`; elsewhere, Context7 or
a quick probe in the project.

- **Rendering and data fetching** — where data loads (server, client, both), what is cached, for how long, and how
  to invalidate after a mutation.
- **Router APIs** — file conventions, params, navigation calls, loading/error boundaries, redirects.
- **Forms and validation** — how the form library binds a schema, and whether the schema library's installed major
  is the one its resolver supports.
- **OpenAPI client generator** — config file name and keys, output path, client flavour, how errors and non-2xx
  statuses are typed.
