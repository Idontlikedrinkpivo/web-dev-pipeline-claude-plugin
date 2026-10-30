"""Serve an iteration's progress pages over local HTTP, so a browser tab reloads them as they change.

    python3 progress_server.py <documentation/plans/<version>>          # start (or reuse); prints the base URL
    python3 progress_server.py <documentation/plans/<version>> --stop   # stop it

A page opened as a file (file://) is not reloaded by the desktop app's built-in browser; the same page served by
http://127.0.0.1 is. The server serves only that one folder, listens on 127.0.0.1 only, runs detached, and is
remembered in <folder>/.progress-server (pid and port), so a second call — after a compaction, from another
stage — reuses it instead of starting another. Ports 8790-8799.

Several projects run their own servers side by side, so a server is never taken on trust: each one answers with
the folder it serves (header X-Dev-Pipeline-Folder), and a server is reused or stopped only when that header names
this folder. A port is taken by binding it; a port another program holds is skipped.

A server keeps the code it was started with for as long as it runs, so it also answers with a fingerprint of that
code (header X-Dev-Pipeline-Code). A server the plugin started before an update is stopped and started again on the
same port when the progress line is next printed — the page's link keeps working, and the new rules (a page redrawn
when its file is newer) take effect without the user doing anything.
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

PORTS = range(8790, 8800)
HEADER = "X-Dev-Pipeline-Folder"
CODE_HEADER = "X-Dev-Pipeline-Code"


def code_id() -> str:
    """A fingerprint of this file and of the page builder it calls: changes whenever the plugin changes them."""
    import hashlib
    h = hashlib.sha1()
    for f in (Path(__file__), Path(__file__).with_name("progress_page.py")):
        try:
            h.update(f.read_bytes())
        except OSError:
            pass
    return h.hexdigest()[:12]


def code_of(port: int) -> str:
    try:
        req = urllib.request.Request(f"http://127.0.0.1:{port}/", method="HEAD")
        with urllib.request.urlopen(req, timeout=1) as r:
            return r.headers.get(CODE_HEADER) or ""
    except Exception as e:
        return (getattr(e, "headers", None) and e.headers.get(CODE_HEADER)) or ""


def serve(port: int, folder: str) -> None:
    """The server itself: http.server for one folder, every answer naming that folder."""
    import functools
    from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

    tag = urllib.parse.quote(folder)
    code = code_id()

    class Handler(SimpleHTTPRequestHandler):
        def do_GET(self) -> None:  # noqa: N802 — http.server's name
            # A page older than its progress file (the file was changed around the hook — from the shell, by a
            # script) is redrawn before it is served, so the user never watches a stale page.
            name = urllib.parse.urlparse(self.path).path.lstrip("/")
            if name.endswith(".html") and "/" not in name:
                md, html = Path(folder) / (name[:-5] + ".md"), Path(folder) / name
                try:
                    if md.is_file() and (not html.exists() or md.stat().st_mtime > html.stat().st_mtime):
                        sys.path.insert(0, str(Path(__file__).resolve().parent))
                        import progress_page
                        progress_page.page(md)
                except Exception:
                    pass  # the old page is still better than none
            super().do_GET()

        def end_headers(self) -> None:
            self.send_header(HEADER, tag)
            self.send_header(CODE_HEADER, code)
            self.send_header("Cache-Control", "no-store")
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


def main() -> None:
    if sys.argv[1:2] == ["--serve"]:
        serve(int(sys.argv[2]), sys.argv[3])
        return
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    folder = Path(sys.argv[1]).resolve()
    state = folder / ".progress-server"
    pid = port = None
    if state.exists():
        try:
            pid, port = (int(x) for x in state.read_text().split()[:2])
        except ValueError:
            pid = port = None
    ours = bool(port) and serves(port, folder)
    if not ours and pid and legacy(pid, folder):
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
    if ours and pid and code_of(port) != code_id():  # started by an earlier plugin version: restart, same port
        try:
            os.kill(pid, signal.SIGTERM)
            for _ in range(30):
                os.kill(pid, 0)
                time.sleep(0.1)
        except OSError:
            pass
        ours = False
    if ours:
        print(f"http://127.0.0.1:{port}/")
        return
    for p in sorted((p for p in PORTS if free(p)), key=lambda x: x != port):  # the old port first
        proc = subprocess.Popen([sys.executable, __file__, "--serve", str(p), str(folder)], stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL, start_new_session=True)
        for _ in range(30):
            if proc.poll() is not None or serves(p, folder):
                break
            time.sleep(0.1)
        if proc.poll() is None and serves(p, folder):
            state.write_text(f"{proc.pid} {p}\n")
            print(f"http://127.0.0.1:{p}/")
            return
        if proc.poll() is None:
            proc.terminate()
    sys.exit(f"no free port in {PORTS.start}-{PORTS.stop - 1}")


if __name__ == "__main__":
    main()
