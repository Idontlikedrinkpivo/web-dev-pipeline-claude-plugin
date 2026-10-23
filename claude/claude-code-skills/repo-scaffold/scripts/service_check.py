"""The scaffold's gate for what the platform does to a service: probe it, scrape it, read its logs, stop it.

    python3 service_check.py --port 3000 -- node dist/src/index.js
    python3 service_check.py --port 8000 --expect-ready -- .venv/bin/python -m <package>.bootstrap.serve
    python3 service_check.py --port 3000 --shutdown-timeout 25 --start-timeout 60 -- <server command...>

Start the server process itself, not a wrapper such as `npm start` or `uv run`: SIGTERM goes to the process this
script started, and a wrapper may not pass it on or may change the exit code. The process inherits the environment,
with LOG_LEVEL=info and SHUTDOWN_TIMEOUT_SEC=<--shutdown-timeout> set, so the check sees the request lines and holds
the app to the timeout it was given.

Checks, each printed as `ok` or `FAIL` (`repo-scaffold` -> SKILL.md §5, Quality gate 3):
  1. GET /health/live -> 200 {"status": "ok"} in under a second;
  2. GET /health/ready -> 200 {"status": "ready"}, or 503 {"status": "not ready", "checks": {...}} (no database
     here); with --expect-ready only 200; in under 2.5 s (the database ping is bounded to 2 s);
  3. GET /metrics -> 200 (a redirect is a failure: Prometheus is given this exact path), Prometheus text naming
     http_request_duration_seconds;
  4. X-Request-Id sent with a request comes back in the response header, and a log line carries it as request_id;
  5. SIGTERM -> exit code 0 within --shutdown-timeout + 5 s;
  6. every line the process wrote to stdout and stderr is one JSON object with time (ISO-8601, UTC), level (a
     word), msg and logger. Node's own `(node:<pid>) ...Warning` lines are skipped: the runtime writes them, not the
     app's logger.
Exit 0 when every check passes, 1 otherwise. Standard library only.
"""
from __future__ import annotations

import argparse
import json
import os
import signal
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import IO, Any, Dict, List, Optional, Tuple

GRACE_SEC = 5
LIVE_LIMIT_SEC = 1.0
READY_LIMIT_SEC = 2.5
LOG_FIELDS = ("time", "level", "msg", "logger")
RUNTIME_NOISE = ("(node:", "(Use `node")


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args: Any, **kwargs: Any) -> None:  # a 3xx comes back as an HTTPError
        return None


OPENER = urllib.request.build_opener(_NoRedirect)


@dataclass
class Answer:
    status: int
    headers: Dict[str, str]
    body: str
    seconds: float

    def json(self) -> Any:
        try:
            return json.loads(self.body)
        except ValueError:
            return None

    def show(self) -> str:
        return f"{self.status} {self.body[:200]!r} in {self.seconds:.2f} s"


def get(port: int, path: str, request_id: Optional[str] = None, timeout: float = 5.0) -> Optional[Answer]:
    request = urllib.request.Request(f"http://127.0.0.1:{port}{path}")
    if request_id is not None:
        request.add_header("X-Request-Id", request_id)
    started = time.monotonic()
    try:
        with OPENER.open(request, timeout=timeout) as response:
            body = response.read().decode("utf-8", "replace")
            headers = {k.lower(): v for k, v in response.headers.items()}
            return Answer(response.status, headers, body, time.monotonic() - started)
    except urllib.error.HTTPError as error:
        body = error.read().decode("utf-8", "replace")
        headers = {k.lower(): v for k, v in error.headers.items()}
        return Answer(error.code, headers, body, time.monotonic() - started)
    except (urllib.error.URLError, OSError):  # not listening yet, or reset
        return None


class Output:
    """Everything the process writes, line by line, from both streams."""

    def __init__(self) -> None:
        self.lines: List[Tuple[str, str]] = []
        self._lock = threading.Lock()
        self._threads: List[threading.Thread] = []

    def follow(self, name: str, pipe: IO[bytes]) -> None:
        thread = threading.Thread(target=self._pump, args=(name, pipe), daemon=True)
        thread.start()
        self._threads.append(thread)

    def _pump(self, name: str, pipe: IO[bytes]) -> None:
        for raw in iter(pipe.readline, b""):
            with self._lock:
                self.lines.append((name, raw.decode("utf-8", "replace").rstrip("\r\n")))
        pipe.close()

    def join(self) -> None:
        for thread in self._threads:
            thread.join(timeout=5)

    def tail(self, count: int = 25) -> str:
        with self._lock:
            return "\n".join(f"  {name}: {line}" for name, line in self.lines[-count:])


class Report:
    def __init__(self) -> None:
        self.failed = 0
        self.total = 0

    def check(self, passed: bool, text: str) -> None:
        self.total += 1
        self.failed += 0 if passed else 1
        print(("ok    " if passed else "FAIL  ") + text, flush=True)


def wait_until_live(port: int, process: subprocess.Popen, deadline: float) -> bool:
    while time.monotonic() < deadline:
        if process.poll() is not None:
            return False
        if get(port, "/health/live", timeout=1.0) is not None:
            return True
        time.sleep(0.3)
    return False


def check_live(report: Report, port: int, request_id: str) -> None:
    answer = get(port, "/health/live", request_id)
    if answer is None:
        report.check(False, "GET /health/live: no answer")
        return
    report.check(
        answer.status == 200 and answer.json() == {"status": "ok"} and answer.seconds < LIVE_LIMIT_SEC,
        f'GET /health/live -> 200 {{"status":"ok"}} under {LIVE_LIMIT_SEC:.0f} s (got {answer.show()})',
    )
    echoed = answer.headers.get("x-request-id")
    report.check(echoed == request_id, f"X-Request-Id echoed in the response (sent {request_id}, got {echoed})")


def check_ready(report: Report, port: int, expect_ready: bool) -> None:
    answer = get(port, "/health/ready")
    if answer is None:
        report.check(False, "GET /health/ready: no answer")
        return
    body = answer.json()
    is_ready = answer.status == 200 and body == {"status": "ready"}
    not_ready = (
        answer.status == 503 and isinstance(body, dict) and body.get("status") == "not ready"
        and isinstance(body.get("checks"), dict)
    )
    expected = '200 {"status":"ready"}' if expect_ready else '200 {"status":"ready"} or 503 {"status":"not ready",...}'
    passed = (is_ready or (not_ready and not expect_ready)) and answer.seconds < READY_LIMIT_SEC
    report.check(passed, f"GET /health/ready -> {expected} under {READY_LIMIT_SEC} s (got {answer.show()})")


def check_metrics(report: Report, port: int) -> None:
    answer = get(port, "/metrics")
    if answer is None:
        report.check(False, "GET /metrics: no answer")
        return
    passed = (
        answer.status == 200 and answer.headers.get("content-type", "").startswith("text/plain")
        and "http_request_duration_seconds" in answer.body
    )
    shown = f"{answer.status}, {answer.headers.get('content-type')}, {len(answer.body)} bytes"
    report.check(passed, f"GET /metrics -> 200 Prometheus text with http_request_duration_seconds (got {shown})")


def stop(report: Report, process: subprocess.Popen, timeout_sec: int) -> None:
    started = time.monotonic()
    process.send_signal(signal.SIGTERM)
    try:
        code = process.wait(timeout=timeout_sec + GRACE_SEC)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait()
        report.check(False, f"SIGTERM -> still running after {timeout_sec + GRACE_SEC} s, killed")
        return
    took = time.monotonic() - started
    report.check(code == 0, f"SIGTERM -> exit 0 within {timeout_sec + GRACE_SEC} s (got exit {code} after {took:.1f} s)")


def is_utc_iso(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    try:
        moment = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return False
    return moment.utcoffset() == timedelta(0)


def log_problem(line: str) -> Optional[str]:
    try:
        entry = json.loads(line)
    except ValueError:
        return "not JSON"
    if not isinstance(entry, dict):
        return "not a JSON object"
    missing = [name for name in LOG_FIELDS if name not in entry]
    if missing:
        return "no " + ", ".join(missing)
    if not is_utc_iso(entry["time"]):
        return f"time {entry['time']!r} is not ISO-8601 UTC"
    if not isinstance(entry["level"], str):
        return f"level {entry['level']!r} is not a word"
    return None


def check_logs(report: Report, output: Output, request_id: str) -> None:
    bad: List[str] = []
    carried = False
    for name, line in output.lines:
        if not line.strip() or line.startswith(RUNTIME_NOISE):
            continue
        problem = log_problem(line)
        if problem is not None:
            bad.append(f"  {name}: {problem}: {line[:160]}")
            continue
        carried = carried or json.loads(line).get("request_id") == request_id
    count = len([1 for _, line in output.lines if line.strip()])
    report.check(not bad, f"every log line is JSON with {', '.join(LOG_FIELDS)} ({count} lines, {len(bad)} bad)")
    for shown in bad[:5]:
        print(shown)
    report.check(carried, f"a log line carries request_id {request_id} (the request to an unknown path)")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--port", type=int, required=True)
    parser.add_argument("--shutdown-timeout", type=int, default=25, help="SHUTDOWN_TIMEOUT_SEC (default 25)")
    parser.add_argument("--start-timeout", type=int, default=60, help="seconds to wait for /health/live")
    parser.add_argument("--expect-ready", action="store_true", help="the database is up: /health/ready must be 200")
    parser.add_argument("command", nargs=argparse.REMAINDER, help="-- <the server command>")
    args = parser.parse_args()
    command = args.command[1:] if args.command[:1] == ["--"] else args.command
    if not command:
        parser.error("give the server command after --")

    env = dict(os.environ, LOG_LEVEL="info", SHUTDOWN_TIMEOUT_SEC=str(args.shutdown_timeout))
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
    output = Output()
    output.follow("stdout", process.stdout)  # type: ignore[arg-type]
    output.follow("stderr", process.stderr)  # type: ignore[arg-type]
    report = Report()

    if not wait_until_live(args.port, process, time.monotonic() + args.start_timeout):
        if process.poll() is None:
            process.kill()
            process.wait()
        state = f"exited with {process.returncode}" if process.returncode is not None else "killed"
        output.join()
        print(f"FAIL  GET /health/live never answered on port {args.port} within {args.start_timeout} s ({state})")
        print(output.tail())
        return 1

    tag = uuid.uuid4().hex[:12]
    check_live(report, args.port, f"service-check-live-{tag}")
    check_ready(report, args.port, args.expect_ready)
    check_metrics(report, args.port)
    unknown_id = f"service-check-unknown-{tag}"
    unknown = get(args.port, f"/service-check-unknown-{tag}", unknown_id)
    echoed = None if unknown is None else unknown.headers.get("x-request-id")
    report.check(echoed == unknown_id, f"X-Request-Id echoed on a 404 too (sent {unknown_id}, got {echoed})")
    time.sleep(0.3)  # let the request lines reach the pipe before the stop
    stop(report, process, args.shutdown_timeout)
    output.join()
    check_logs(report, output, unknown_id)

    print(f"service check: {report.total - report.failed} of {report.total} passed")
    if report.failed:
        print("last lines of the process:")
        print(output.tail())
    return 1 if report.failed else 0


if __name__ == "__main__":
    sys.exit(main())
