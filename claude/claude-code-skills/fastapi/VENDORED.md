# Vendored

Source: the official FastAPI agent skill, https://github.com/fastapi/fastapi, file
`fastapi/.agents/skills/fastapi/SKILL.md` (MIT, `LICENSE` in this folder, copied from the repository root). The
upstream commit was not recorded.

Adapted for this plugin; parts of the text follow the original closely:

- added: which layout governs (the architecture's router factories wired in `bootstrap/`, or the existing repo),
  and the contract from `documentation/api/openapi.yaml` with problem+json errors;
- kept as short conventions: the `fastapi` CLI, `Annotated`, dependency aliases, no Ellipsis, no `RootModel`, the
  return type, self-contained routers, one function per operation, `def` unless sure, tooling and libraries;
- version facts (streaming, serving a built frontend, CLI entrypoint config, `yield` dependencies) became the
  checklist in `references/version-checks.md` — verify against the installed version;
- added from this plugin: the problem+json error handlers, auth and settings (`references/jwt-auth.md`), the
  contract test, the service endpoints, JSON logs and shutdown (`references/service-endpoints.md` — the container
  starts through `bootstrap/serve.py` instead of the original's `fastapi run`), «The reviewer checks»; the database
  layer is left to `fastapi-sqlalchemy`.
