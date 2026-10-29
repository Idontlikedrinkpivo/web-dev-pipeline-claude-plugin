"""Serve the documentation site over local HTTP, so the desktop app's built-in browser shows it whole.

    python3 site_server.py [<site folder>]          # start (or reuse); prints the address of index.html
    python3 site_server.py [<site folder>] --stop   # stop it

The built-in browser opens a page given as a file without its stylesheet and scripts — no menu, no search; served
from http://127.0.0.1 the site works as in any browser. The server serves only the site folder (default
documentation/_web-docs), listens on 127.0.0.1 only, runs detached, and is remembered outside the committed site, in
<git dir>/pipeline-work/site-server, so a second call reuses it. Ports 8800-8809.

Several projects run their own servers side by side, so a server is never taken on trust: each one answers with
the folder it serves (header X-Dev-Pipeline-Folder), and a server is reused or stopped only when that header names
this site. A port is taken by binding it; a port another program holds is skipped.
"""
from __future__ import annotations

import os
import signal
import socket
import subprocess
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

PORTS = range(8800, 8810)
HEADER = "X-Dev-Pipeline-Folder"


def serve(port: int, folder: str) -> None:
    """The server itself: http.server for one folder, every answer naming that folder."""
    import functools
    from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

    tag = urllib.parse.quote(folder)

    class Handler(SimpleHTTPRequestHandler):
        def end_headers(self) -> None:
            self.send_header(HEADER, tag)
            self.send_header("Cache-Control", "no-store")  # a rebuilt site shows at once, without a forced reload
            super().end_headers()

        def log_message(self, *args) -> None:
            pass

    ThreadingHTTPServer(("127.0.0.1", port), functools.partial(Handler, directory=folder)).serve_forever()


def serves(port: int, folder: Path) -> bool:
    """True when the server on this port is ours and serves this folder."""
    try:
        req = urllib.request.Request(f"http://127.0.0.1:{port}/", method="HEAD")
        with urllib.request.urlopen(req, timeout=1) as r:
            tag = r.headers.get(HEADER)
    except Exception as e:
        tag = getattr(e, "headers", None) and e.headers.get(HEADER)
    return bool(tag) and urllib.parse.unquote(tag) == str(folder)


def legacy(pid: int, folder: Path) -> bool:
    """A server an earlier version of this script started for this folder: plain http.server, no header."""
    try:
        cmd = subprocess.run(["ps", "-p", str(pid), "-o", "command="], capture_output=True, text=True,
                             timeout=5).stdout
    except Exception:
        return False
    return "http.server" in cmd and str(folder) in cmd


def free(port: int) -> bool:
    with socket.socket() as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # as http.server binds: a closed port is free
        try:
            s.bind(("127.0.0.1", port))
            return True
        except OSError:
            return False


def state_file(site: Path) -> Path:
    try:
        git = subprocess.run(["git", "-C", str(site), "rev-parse", "--git-dir"], capture_output=True, text=True,
                             timeout=10).stdout.strip()
    except Exception:
        git = ""
    base = (site / git) if git and not os.path.isabs(git) else Path(git) if git else site.parent
    d = base.resolve() / "pipeline-work"
    d.mkdir(parents=True, exist_ok=True)
    return d / "site-server"


def main() -> None:
    if sys.argv[1:2] == ["--serve"]:
        serve(int(sys.argv[2]), sys.argv[3])
        return
    args = [a for a in sys.argv[1:] if a != "--stop"]
    site = Path(args[0] if args else "documentation/_web-docs").resolve()
    if not (site / "index.html").exists():
        sys.exit(f"no site at {site} — build it first (build_site.py)")
    state = state_file(site)
    pid = port = None
    if state.exists():
        try:
            pid, port = (int(x) for x in state.read_text().split()[:2])
        except ValueError:
            pid = port = None
    ours = bool(port) and serves(port, site)
    if not ours and pid and legacy(pid, site):
        try:
            os.kill(pid, signal.SIGTERM)  # started by an earlier version: replaced by one that names its folder
            for _ in range(30):
                os.kill(pid, 0)
                time.sleep(0.1)
        except OSError:
            pass
    if "--stop" in sys.argv:
        if ours and pid:
            try:
                os.kill(pid, signal.SIGTERM)
            except OSError:
                pass
        state.unlink(missing_ok=True) if sys.version_info >= (3, 8) else None
        print("stopped")
        return
    if ours:
        print(f"http://127.0.0.1:{port}/index.html")
        return
    for p in (p for p in PORTS if free(p)):
        proc = subprocess.Popen([sys.executable, __file__, "--serve", str(p), str(site)], stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL, start_new_session=True)
        for _ in range(30):
            if proc.poll() is not None or serves(p, site):
                break
            time.sleep(0.1)
        if proc.poll() is None and serves(p, site):
            state.write_text(f"{proc.pid} {p} {site}\n")
            print(f"http://127.0.0.1:{p}/index.html")
            return
        if proc.poll() is None:
            proc.terminate()
    sys.exit(f"no free port in {PORTS.start}-{PORTS.stop - 1}")


if __name__ == "__main__":
    main()
