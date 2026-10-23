# Service endpoints, logs and shutdown — the Fastify form

Read this when writing or changing `bootstrap/` (`repo-scaffold` writes it once), the logger options, the entry
point or a readiness check. What the platform expects of every service is fixed in `repo-scaffold` → SKILL.md §5;
this is how Fastify does it. The file names are the architecture §5 tree's — `bootstrap/…` and `src/index.ts`
below are only the defaults (a flat tree has, say, `src/server.ts`, `src/service-routes.ts`); adding these files to
an existing project is a changed architecture decision (`pipeline` → `references/decision-changes.md`).

## The logger and the request id — inside `buildServer()` in `bootstrap/server.ts`

```typescript
import { randomUUID } from "node:crypto"

import Fastify, { LogController } from "fastify"

const app = Fastify({
  logger: {
    level: deps.logLevel, // LOG_LEVEL, default "info"; the tests pass "silent"
    base: { logger: "<project>" }, // the logger name; replaces pid and hostname
    timestamp: () => `,"time":"${new Date().toISOString()}"`, // ISO-8601 UTC, not epoch milliseconds
    formatters: { level: (label) => ({ level: label }) }, // "info", not 30
  },
  requestIdHeader: "x-request-id", // the caller's id when present...
  genReqId: () => randomUUID(), // ...else a new one
  logController: new LogController({ requestIdLogLabel: "request_id" }),
})
app.addHook("onRequest", (request, reply, done) => {
  reply.header("x-request-id", request.id) // echoed, on errors and 404s too
  done()
})
registerServiceRoutes(app, deps.ready) // before the area routes, so the histogram hook covers them
```

- Every line is then `{"level","time","logger","msg"}`, plus `request_id` inside a request and `err` (`type`,
  `message`, `stack` — pino's serializer) when an error is logged as `{ err }`.
- A module that logs on its own takes a child logger, `app.log.child({ logger: "<area>.<module>" })`, so the
  `logger` field says where a line came from. Code logs through `request.log` or such a child, never `console`.
- No `transport` and no `pino-pretty` in the app's options: a local `dev` script may pipe through it
  (`tsx watch src/index.ts | pino-pretty`), so every other run writes JSON.
- A log line carries ids and codes — never a secret, a token, a password or personal data: no request body, no
  `authorization` or `cookie` header (the default `req` serializer logs neither; keep it that way).
- `LogController` exists in recent Fastify 5 releases; an older one takes `requestIdLogLabel` as a top-level option
  (`version-checks.md`).

## The service routes and the histogram — `bootstrap/service-routes.ts`

```typescript
import type { FastifyInstance, LogLevel } from "fastify"
import { collectDefaultMetrics, Histogram, Registry } from "prom-client"

export type CheckState = "up" | "down"
/** Each store the app cannot serve without, by name: `{ db: "up" }`. Never a third-party API. */
export type ReadinessChecks = () => Promise<Record<string, CheckState>>

const SERVICE_PATHS = new Set(["/health/live", "/health/ready", "/metrics"])
/** The levels quieter than warn: the service routes follow the app down to them. */
const QUIETER_THAN_WARN: Partial<Record<string, LogLevel>> = { error: "error", fatal: "fatal", silent: "silent" }

/** "up" when the check settles within the bound, "down" when it fails or hangs — a hung pool must not hang the probe. */
export async function probe(check: () => Promise<unknown>, ms = 2000): Promise<CheckState> {
  let timer: NodeJS.Timeout | undefined
  const late = new Promise<CheckState>((resolve) => {
    timer = setTimeout(resolve, ms, "down")
  })
  try {
    return await Promise.race([check().then(() => "up" as const, () => "down" as const), late])
  } finally {
    clearTimeout(timer)
  }
}

/** /health/live, /health/ready, /metrics and the request-duration histogram. Register before the area routes. */
export function registerServiceRoutes(app: FastifyInstance, ready: ReadinessChecks): void {
  const registry = new Registry() // one per app: tests build many servers, and the global one refuses a second metric
  collectDefaultMetrics({ register: registry })
  const duration = new Histogram({
    name: "http_request_duration_seconds",
    help: "HTTP request duration by route template",
    labelNames: ["method", "route", "status_code"] as const,
    registers: [registry],
  })
  app.addHook("onResponse", (request, reply, done) => {
    const route = request.routeOptions.url ?? "unmatched" // the template; never request.url — no unbounded labels
    if (!SERVICE_PATHS.has(route)) {
      duration.observe({ method: request.method, route, status_code: String(reply.statusCode) }, reply.elapsedTime / 1000)
    }
    done()
  })

  // Probes every few seconds would flood the log: the service routes log at warn, or quieter when the app is
  // (a route's own level overrides the app's, so the tests' "silent" must reach it too).
  const quiet = { logLevel: QUIETER_THAN_WARN[app.log.level] ?? "warn" }
  app.get("/health/live", quiet, () => ({ status: "ok" })) // touches nothing: a database outage must not restart every pod
  app.get("/health/ready", quiet, async (request, reply) => {
    const checks = await ready()
    if (!Object.values(checks).includes("down")) return { status: "ready" }
    request.log.warn({ checks }, "not ready")
    return reply.code(503).send({ status: "not ready", checks })
  })
  app.get("/metrics", quiet, async (_request, reply) => reply.type(registry.contentType).send(await registry.metrics()))
}
```

- The three routes answer their bodies themselves: they are status answers outside the contract, not errors, so
  the global error handler and the Problem body do not apply. No auth hook covers them — register the auth hook on
  the API prefix, not the root.
- They are in the contract test's `NOT_IN_CONTRACT`; no spec operation describes them.
- A new store the app cannot serve without (object storage, a queue) adds one key to `ready`; a partner's API never
  does — its outage would take every pod out of rotation at once. A new route needs nothing here.

## The entry point — the one file that calls `listen` (`src/index.ts`)

```typescript
import { Pool } from "pg" // the driver §1 «Стек» names

import { loadConfig } from "./bootstrap/config.js"
import { buildServer } from "./bootstrap/server.js"
import { probe } from "./bootstrap/service-routes.js"

const config = loadConfig(process.env)
const pool = config.databaseUrl === undefined ? undefined : new Pool({ connectionString: config.databaseUrl })
const app = buildServer({
  logLevel: config.logLevel,
  ready: async () => ({ db: pool === undefined ? "down" : await probe(() => pool.query("select 1")) }),
  // ...the dependencies the routes take
})
app.addHook("onClose", async () => {
  await pool?.end() // after the last in-flight request
})
await app.listen({ host: "0.0.0.0", port: config.port })

function shutDown(signal: NodeJS.Signals): void {
  app.log.info({ signal }, "shutting down")
  setTimeout(() => {
    app.log.error({ signal }, `shutdown took longer than ${config.shutdownTimeoutSec} s`)
    process.exit(1)
  }, config.shutdownTimeoutSec * 1000).unref()
  app.close().then(
    () => process.exit(0),
    (err: unknown) => {
      app.log.error({ err }, "shutdown failed")
      process.exit(1)
    },
  )
}
process.once("SIGTERM", shutDown)
process.once("SIGINT", shutDown)
```

- Node as PID 1 has no default SIGTERM handling: without these handlers the container ignores the stop and is
  killed at the end of the grace period, mid-request.
- `app.close()` stops accepting (a request that arrives meanwhile gets 503), finishes the in-flight ones, then runs
  the `onClose` hooks — the pool ends there. The timer exits 1 past `SHUTDOWN_TIMEOUT_SEC` and is `unref`'d, so it
  never holds a finished process open.
- A system without a database passes `ready: () => Promise.resolve({})` — ready as soon as it listens.

## Configuration

`LOG_LEVEL` (optional; one of pino's levels, default `info`) and `SHUTDOWN_TIMEOUT_SEC` (optional; a positive
integer, default `25` — under Kubernetes' default 30 s grace period) are read and validated in the config module
with the other variables, and listed in `.env.example`.

## The check

`repo-scaffold`'s quality gate runs `repo-scaffold/scripts/service_check.py` against the started entry point: the
three paths, the request id echoed and logged, JSON on every line, exit 0 on SIGTERM within the timeout + 5 s. Run
it again after changing any of the code above.
