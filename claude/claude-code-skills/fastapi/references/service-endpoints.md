# Service endpoints, logs and shutdown — the FastAPI form

Read this when writing or changing `bootstrap/` (`repo-scaffold` writes it once), the logging setup, the production
entry or a readiness check. What the platform expects of every service is fixed in `repo-scaffold` → SKILL.md §5;
this is how FastAPI and uvicorn do it. The file names are the architecture §5 tree's — `bootstrap/…` below is
only the default; adding these files to an existing project is a changed architecture decision (`pipeline` →
`references/decision-changes.md`).

## JSON logs, the request id, the histogram, the three routes — `bootstrap/observability.py`

```python
"""JSON logs, the request id, the request-duration histogram and the three service routes."""

from __future__ import annotations

import asyncio
import json
import logging
import sys
import time
import uuid
from contextvars import ContextVar
from datetime import UTC, datetime

from fastapi import APIRouter, Response
from fastapi.responses import JSONResponse
from prometheus_client import CONTENT_TYPE_LATEST, REGISTRY, Histogram, generate_latest
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncEngine
from starlette.datastructures import MutableHeaders
from starlette.types import ASGIApp, Message, Receive, Scope, Send

REQUEST_ID: ContextVar[str | None] = ContextVar("request_id", default=None)
SERVICE_PATHS = frozenset({"/health/live", "/health/ready", "/metrics"})
REQUEST_DURATION = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration by route template",
    ("method", "route", "status_code"),
)
_RECORD_FIELDS = frozenset(vars(logging.makeLogRecord({}))) | {"message", "asctime", "color_message"}
logger = logging.getLogger(__name__)
access_log = logging.getLogger("http.access")


class JsonFormatter(logging.Formatter):
    """One JSON object per record: time, level, msg, logger, request_id, the `extra` fields, err for an exception."""

    def format(self, record: logging.LogRecord) -> str:
        entry: dict[str, object] = {
            "time": datetime.fromtimestamp(record.created, UTC).isoformat(timespec="milliseconds"),
            "level": record.levelname.lower(),
            "msg": record.getMessage(),
            "logger": record.name,
            "request_id": REQUEST_ID.get(),
        }
        entry.update({k: v for k, v in vars(record).items() if k not in _RECORD_FIELDS and k not in entry})
        if record.exc_info is not None and record.exc_info[1] is not None:
            error = record.exc_info[1]
            entry["err"] = {
                "type": type(error).__name__,
                "message": str(error),
                "stack": self.formatException(record.exc_info),
            }
        return json.dumps(entry, ensure_ascii=False, default=str)


def configure_logging(level: str) -> None:
    """Before the server starts: every logger, uvicorn's included, writes JSON lines to stdout."""
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())
    logging.basicConfig(level=level.upper(), handlers=[handler], force=True)
    for name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
        logging.getLogger(name).handlers.clear()
        logging.getLogger(name).propagate = True


class RequestContext:
    """Pure ASGI: takes X-Request-Id (or makes one) and echoes it; times the request by its route template."""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        incoming = dict(scope["headers"]).get(b"x-request-id")
        request_id = incoming.decode("latin-1") if incoming else uuid.uuid4().hex
        token = REQUEST_ID.set(request_id)
        status = 500
        started = time.perf_counter()

        async def send_with_id(message: Message) -> None:
            nonlocal status
            if message["type"] == "http.response.start":
                status = message["status"]
                MutableHeaders(scope=message).append("x-request-id", request_id)
            await send(message)

        try:
            await self.app(scope, receive, send_with_id)
        finally:
            route = getattr(scope.get("route"), "path", None) or "unmatched"  # the template, never the raw path
            if route not in SERVICE_PATHS:  # probes and scrapes would drown the real traffic
                elapsed = time.perf_counter() - started
                REQUEST_DURATION.labels(scope["method"], route, str(status)).observe(elapsed)
                access_log.info(
                    "%s %s %d", scope["method"], route, status, extra={"duration_ms": round(elapsed * 1000)}
                )
            REQUEST_ID.reset(token)


async def database_ready(engine: AsyncEngine | None) -> bool:
    if engine is None:  # no DATABASE_URL: the app cannot serve
        return False
    try:
        async with asyncio.timeout(2), engine.connect() as connection:
            await connection.execute(text("SELECT 1"))
    except (TimeoutError, OSError, SQLAlchemyError) as error:
        logger.warning("database not ready: %s", type(error).__name__)
        return False
    return True


def build_service_router(engine: AsyncEngine | None) -> APIRouter:
    """/health/live, /health/ready, /metrics: outside the contract and outside auth."""
    router = APIRouter(include_in_schema=False)

    @router.get("/health/live")
    async def live() -> dict[str, str]:
        return {"status": "ok"}  # touches nothing: a database outage must not restart every pod

    @router.get("/health/ready")
    async def ready() -> JSONResponse:
        checks = {"db": "up" if await database_ready(engine) else "down"}
        if "down" in checks.values():
            return JSONResponse({"status": "not ready", "checks": checks}, status_code=503)
        return JSONResponse({"status": "ready"})

    @router.get("/metrics")
    def metrics() -> Response:
        return Response(generate_latest(REGISTRY), media_type=CONTENT_TYPE_LATEST)

    return router
```

- Every line is then `{"time","level","msg","logger","request_id"}`, plus the record's `extra` fields
  (`logger.info("booking rejected", extra={"event": "booking_rejected", "code": code})`) and `err` when logged with
  `exc_info` (`logger.exception(...)`). Code logs through `logging.getLogger(__name__)`, never `print` (Ruff `T20`).
- A log line carries ids and codes — never a secret, a token, a password or personal data: no request body, no
  header values, no query string (the access line names the route template, not the raw path).
- The middleware is pure ASGI, so the request id is set before the router runs and still set when the response
  goes out; the access line is the app's own (`access_log=False` below), with the template and the duration.
- `/metrics` is a route, not `app.mount("/metrics", make_asgi_app())`: a mount matches only below its prefix, so
  `/metrics` itself would answer a 307 to `/metrics/`.
- The three routes answer their bodies themselves: they are status answers outside the contract, not errors, so the
  problem+json handlers do not apply. No auth dependency covers them — put auth on the API routers, not on the app.
- A system without a database drops the `db` check (`checks = {}` is ready). A new store the app cannot serve
  without (object storage, a queue) adds one key; a partner's API never does — its outage would take every pod out
  of rotation at once.

## The app factory — `bootstrap/main.py`

```python
def create_app(settings: Settings) -> FastAPI:
    engine = create_async_engine(settings.database_url) if settings.database_url else None

    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncIterator[None]:
        yield
        if engine is not None:
            await engine.dispose()  # after uvicorn has finished the in-flight requests

    app = FastAPI(lifespan=lifespan)
    app.add_middleware(RequestContext)
    app.include_router(build_service_router(engine))
    # ...the area routers, the problem+json handlers
    return app


app = create_app(Settings())
```

## The production entry — `bootstrap/serve.py`, run as `python -m <package>.bootstrap.serve`

```python
"""The production entry: JSON logs first, then uvicorn with the shutdown timeout."""

from __future__ import annotations

import signal
from types import FrameType

import uvicorn

from <package>.bootstrap.observability import configure_logging
from <package>.bootstrap.settings import Settings


def _ignore(_signum: int, _frame: FrameType | None) -> None:
    """What uvicorn calls after its graceful shutdown: returning lets the process exit 0."""


def main() -> None:
    settings = Settings()
    configure_logging(settings.log_level)  # before uvicorn starts, so its own lines are JSON too
    # uvicorn re-raises the signal after a graceful shutdown; under the default handler that ends the process with
    # 143. It restores and calls the handler found at start, so a no-op one makes the exit 0.
    for sig in (signal.SIGTERM, signal.SIGINT):
        signal.signal(sig, _ignore)
    uvicorn.run(
        "<package>.bootstrap.main:app",
        host="0.0.0.0",  # inside a container
        port=settings.port,
        workers=1,  # one process per container; replicas scale it
        log_config=None,  # keep the JSON handler configured above
        access_log=False,  # RequestContext writes the access line, with the route template
        timeout_graceful_shutdown=settings.shutdown_timeout_sec,
    )


if __name__ == "__main__":
    main()
```

- Not `fastapi run`: it installs its own log format and passes no graceful-shutdown timeout to uvicorn
  (`version-checks.md`). `fastapi dev` stays the local run.
- On SIGTERM uvicorn stops accepting, finishes the in-flight requests within `SHUTDOWN_TIMEOUT_SEC`, runs the
  lifespan's shutdown — the engine is disposed there — and returns.
- **Several workers** are the exception, not the default. A run with `workers` above 1 needs `prometheus_client`'s
  multiprocess mode, or each scrape sees one worker's numbers: `PROMETHEUS_MULTIPROC_DIR` pointing at a tmpfs
  emptied before start, and the `/metrics` route building a `CollectorRegistry` with `MultiProcessCollector` per
  scrape instead of serving `REGISTRY`. Say so where the workers are configured.

## Settings

```python
log_level: Literal["debug", "info", "warning", "error"] = "info"  # LOG_LEVEL
shutdown_timeout_sec: PositiveInt = 25  # SHUTDOWN_TIMEOUT_SEC — under Kubernetes' default 30 s grace period
```

Both are optional and listed in `.env.example` with their defaults in the comment.

## The check

`repo-scaffold`'s quality gate runs `repo-scaffold/scripts/service_check.py` against
`.venv/bin/python -m <package>.bootstrap.serve`: the three paths, the request id echoed and logged, JSON on every
line, exit 0 on SIGTERM within the timeout + 5 s. Run it again after changing any of the code above.
