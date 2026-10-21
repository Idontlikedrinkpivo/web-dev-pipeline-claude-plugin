"""Serve the documentation site over local HTTP, so the desktop app's built-in browser shows it whole.

    python3 site_server.py [<site folder>]          # start (or reuse); prints the address of index.html
    python3 site_server.py [<site folder>] --stop   # stop it

The built-in browser opens a page given as a file without its stylesheet and scripts — no menu, no search; served
from http://127.0.0.1 the site works as in any browser. The server serves only the site folder (default
documentation/site), listens on 127.0.0.1 only, runs detached, and is remembered outside the committed site, in
<git dir>/pipeline-work/site-server, so a second call reuses it. Ports 8800-8809; the first free one is taken.
"""
from __future__ import annotations

import os
import signal
import socket
import subprocess
import sys
import time
from pathlib import Path


def alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def answers(port: int) -> bool:
    with socket.socket() as s:
        s.settimeout(0.5)
        return s.connect_ex(("127.0.0.1", port)) == 0


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
    args = [a for a in sys.argv[1:] if a != "--stop"]
    site = Path(args[0] if args else "documentation/site").resolve()
    if not (site / "index.html").exists():
        sys.exit(f"no site at {site} — build it first (build_site.py)")
    state = state_file(site)
    pid = port = None
    if state.exists():
        try:
            pid, port, folder = state.read_text().split(maxsplit=2)
            pid, port = int(pid), int(port)
            if folder.strip() != str(site):
                pid = port = None
        except ValueError:
            pid = port = None
    if "--stop" in sys.argv:
        if pid and alive(pid):
            os.kill(pid, signal.SIGTERM)
        if state.exists():
            state.unlink()
        print("stopped")
        return
    if pid and port and alive(pid) and answers(port):
        print(f"http://127.0.0.1:{port}/index.html")
        return
    port = next((p for p in range(8800, 8810) if not answers(p)), None)
    if port is None:
        sys.exit("no free port in 8800-8809")
    proc = subprocess.Popen([sys.executable, "-m", "http.server", str(port), "--bind", "127.0.0.1",
                             "--directory", str(site)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                            stdin=subprocess.DEVNULL, start_new_session=True)
    for _ in range(20):
        if answers(port):
            break
        time.sleep(0.1)
    state.write_text(f"{proc.pid} {port} {site}\n")
    print(f"http://127.0.0.1:{port}/index.html")


if __name__ == "__main__":
    main()
