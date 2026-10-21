"""Rebuild the documentation site in the background after a document changes; wait for it before a commit.

    python3 rebuild.py <project dir> [--api]   # queue a rebuild (--api: the contract changed, rebuild its page)
    python3 rebuild.py <project dir> --wait    # block until no rebuild runs or is queued

Called by the plugin's PostToolUse hook (hooks/site-rebuild.sh) on every edit under documentation/ — plans/ and the
site itself left out. A pipeline project without a site gets one at its first document (a full build, the API page
too) — not another repository that merely has a documentation/ folder, and not a project whose user declined the
site for good (`docs-site` in documentation/.dev-pipeline.json → skipped). One build
runs at a time: an edit during a build queues exactly one more, so a burst of edits costs two builds, not twenty.
Without --api the bundled contract is reused (bundling it takes seconds to minutes); with it, rebundled. State in <git dir>/pipeline-work/:
site-build.lock (the running worker's pid) and site-build.pending (a queued rebuild, «api» when the contract
changed). The site is swapped in whole at the end of a build, so a reader never sees half of it.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent


def work_dir(root: Path) -> Path:
    try:
        git = subprocess.run(["git", "-C", str(root), "rev-parse", "--git-dir"], capture_output=True, text=True,
                             timeout=10).stdout.strip()
    except Exception:
        git = ""
    base = (root / git) if git and not os.path.isabs(git) else Path(git) if git else root
    d = base.resolve() / "pipeline-work"
    d.mkdir(parents=True, exist_ok=True)
    return d


def alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def running(lock: Path) -> bool:
    try:
        return alive(int(lock.read_text().split()[0]))
    except (OSError, ValueError, IndexError):
        return False


def wanted(root: Path) -> bool:
    """A first site only in a pipeline project (requirements, plans or the plugin stamp under documentation/) — the
    plugin is installed per user, and another repository's documentation/ is not its business — and not when the
    user declined the site for good (upgrade → skip docs-site)."""
    doc = root / "documentation"
    if not any((doc / p).exists() for p in ("requirements", "plans", ".dev-pipeline.json")):
        return False
    try:
        return "docs-site" not in json.loads((doc / ".dev-pipeline.json").read_text()).get("skipped", [])
    except (OSError, ValueError, AttributeError):
        return True


def worker(root: Path, d: Path) -> None:
    lock, pending = d / "site-build.lock", d / "site-build.pending"
    lock.write_text(str(os.getpid()))
    try:
        while pending.exists():
            api = pending.read_text().strip() == "api"
            pending.unlink()
            subprocess.run([sys.executable, str(HERE / "build_site.py"), "--docs", str(root / "documentation"),
                            "--out", str(root / "documentation" / "_site")] + ([] if api else ["--keep-api"]),
                           cwd=root, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=600)
    finally:
        lock.unlink(missing_ok=True) if sys.version_info >= (3, 8) else None


def main() -> None:
    args = sys.argv[1:]
    root = Path(next((a for a in args if not a.startswith("--")), os.getcwd())).resolve()
    first = not (root / "documentation" / "_site" / "index.html").exists()
    if first and not wanted(root):
        return  # no site, and this project is not the pipeline's or declined one
    d = work_dir(root)
    lock, pending = d / "site-build.lock", d / "site-build.pending"
    if "--wait" in args:
        for _ in range(1200):  # up to 10 minutes: a contract rebuild bundles the spec
            if not running(lock) and not pending.exists():
                return
            if not running(lock) and pending.exists():
                break  # queued but no worker: run it now, in the foreground
            time.sleep(0.5)
        if pending.exists() and not running(lock):
            worker(root, d)
        return
    if "--worker" in args:
        worker(root, d)
        return
    api = "--api" in args or first  # the first build makes the API page as well
    if api or not pending.exists() or pending.read_text().strip() != "api":
        pending.write_text("api" if api else "page")
    if not running(lock):
        proc = subprocess.Popen([sys.executable, __file__, str(root), "--worker"], stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL, start_new_session=True, cwd=root)
        lock.write_text(str(proc.pid))  # at once, so the next edit queues instead of starting a second worker


if __name__ == "__main__":
    main()
