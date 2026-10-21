"""Serve an iteration's progress pages over local HTTP, so a browser tab reloads them as they change.

    python3 progress_server.py <documentation/plans/<version>>          # start (or reuse); prints the base URL
    python3 progress_server.py <documentation/plans/<version>> --stop   # stop it

A page opened as a file (file://) is not reloaded by the desktop app's built-in browser; the same page served by
http://127.0.0.1 is. The server serves only that one folder, listens on 127.0.0.1 only, runs detached, and is
remembered in <folder>/.progress-server (pid and port), so a second call — after a compaction, from another
stage — reuses it instead of starting another. Ports 8790-8799; the first free one is taken.
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


def main() -> None:
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    folder = Path(sys.argv[1]).resolve()
    state = folder / ".progress-server"
    pid = port = None
    if state.exists():
        try:
            pid, port = (int(x) for x in state.read_text().split())
        except ValueError:
            pass
    if "--stop" in sys.argv:
        if pid and alive(pid):
            os.kill(pid, signal.SIGTERM)
        state.unlink(missing_ok=True) if sys.version_info >= (3, 8) else None
        print("stopped")
        return
    if pid and port and alive(pid) and answers(port):
        print(f"http://127.0.0.1:{port}/")
        return
    port = next((p for p in range(8790, 8800) if not answers(p)), None)
    if port is None:
        sys.exit("no free port in 8790-8799")
    proc = subprocess.Popen([sys.executable, "-m", "http.server", str(port), "--bind", "127.0.0.1",
                             "--directory", str(folder)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                            stdin=subprocess.DEVNULL, start_new_session=True)
    for _ in range(20):
        if answers(port):
            break
        time.sleep(0.1)
    state.write_text(f"{proc.pid} {port}\n")
    print(f"http://127.0.0.1:{port}/")


if __name__ == "__main__":
    main()
