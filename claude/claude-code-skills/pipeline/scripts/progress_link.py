"""The one line a stage pastes in the chat about its progress: the count and a clickable link to the page.

    python3 progress_link.py <progress file .md>                 # the line; rebuilds the page first
    python3 progress_link.py <progress file .md> --desktop       # in the desktop app: start or reuse the server
    python3 progress_link.py <progress file .md> --count "2 из 5 исправлений"   # another count than the file's

Prints exactly one line, e.g.

    План: 3 из 6 · [progress.html](http://127.0.0.1:8790/progress.html)

The link is always the page beside the file (progress.md -> progress.html), never the Markdown. Its address:
- with --desktop (the session has the built-in browser), the progress server's http://127.0.0.1:<port>/ address
  (progress_server.py, started or reused): a page opened as a file is not reloaded there, a served one is;
- without it, the same server's address when one already runs for this folder, else the page's path from the
  repository root, which the user's own browser reloads by itself.
--desktop is remembered beside the file (.progress-desktop): a later call without it — after a context compaction
dropped the flag — still starts or reuses the server, so the link never falls back to a file path.

A bar that disagrees with the count line (a file edited from the shell, so the page and the bar were not redrawn)
is named on stderr; the line on stdout stays as it is.

The count is the file's count line (the line under its bar, «Сделано: 3 из 6»), without its label; the label is
the stage's name. Paste the line as printed — never write the link by hand. Standard library only.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

# the chat label per progress file (pipeline → references/progress-files.md → Which stages keep one)
LABEL = {
    "progress.md": "План", "progress-design.md": "Макеты", "progress-screen-specs.md": "ТЗ на экраны",
    "progress-test-cases.md": "Тест-кейсы", "test-run.md": "Проверка через интерфейс",
    "security-audit.md": "Аудит безопасности", "progress-architecture.md": "Архитектура",
    "progress-scaffold.md": "Каркас", "progress-deploy.md": "Релиз", "progress-mutation.md": "Мутации",
}


def rebuild(md: Path) -> None:
    """The page beside the file, as the hook would build it; a failure here never blocks the line."""
    try:
        import progress_page  # noqa: WPS433 — beside this script
        progress_page.page(md)
    except Exception:
        subprocess.run([sys.executable, str(HERE / "progress_page.py"), str(md)], capture_output=True)


def count_of(md: Path) -> str:
    text = md.read_text(encoding="utf-8", errors="replace")
    try:
        import progress_page   # the files whose count the page computes from the rows
        if md.name in progress_page.DERIVED:
            got = progress_page.derived(text)
            if got:
                return re.sub(r"^Готово:\s*", "", got[1]) + f" · {got[0]}%"
    except Exception:
        pass
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    line = ""
    for i, l in enumerate(lines):  # the count line sits right under the bar's block
        if re.search(r"[█░]{5,}", l):
            after = [x for x in lines[i + 1:] if not x.startswith("```")]
            line = after[0] if after and re.search(r"\d+\s*из\s*\d+", after[0]) else ""
            break
    if not line:
        line = next((l for l in lines if re.search(r"\d+\s*из\s*\d+", l) and not l.startswith(("|", "#"))), "")
    line = re.sub(r"[*`]", "", line)
    return re.sub(r"^[^:·|]{1,40}:\s*", "", line).strip()  # «Сделано: 3 из 6» -> «3 из 6»


DERIVED_NAMES = {"progress-design.md", "progress-screen-specs.md", "progress-test-cases.md",
                 "progress-architecture.md", "security-audit.md", "progress-scaffold.md", "progress-deploy.md"}


def bar_mismatch(md: Path, count: str) -> str:
    """A warning when the bar's percent is not the count's, else ""."""
    text = md.read_text(encoding="utf-8", errors="replace")
    b = re.search(r"([█░]{20,})\s*(\d+)\s*%", text)
    c = re.search(r"(\d+)\s*из\s*(\d+)", count)
    if md.name in DERIVED_NAMES:   # the page computes this bar from the rows; the file's own bar is not read
        return ""
    if not b or not c or int(c[2]) == 0 or "успешно" in count:  # a test run's bar is the share that passes
        return ""
    want = int(c[1]) * 100 // int(c[2])
    shown = b[1].count("█")
    if abs(shown - want) > 1 or abs(int(b[2]) - want) > 1:
        return (f"progress_link: the bar shows {b[2]}% but the count says {c[1]} из {c[2]} ({want}%) — fix the bar "
                f"with Edit (a file changed from the shell is not redrawn)")
    return ""


def running(folder: Path) -> str | None:
    """The address of a progress server already serving this folder, or None. Starts nothing."""
    try:
        import progress_server
        pid_port = (folder / ".progress-server").read_text().split()[:2]
        port = int(pid_port[1])
        return f"http://127.0.0.1:{port}/" if progress_server.serves(port, folder) else None
    except Exception:
        return None


def start(folder: Path) -> str | None:
    r = subprocess.run([sys.executable, str(HERE / "progress_server.py"), str(folder)], capture_output=True,
                       text=True)
    out = r.stdout.strip().splitlines()
    return out[-1] if r.returncode == 0 and out and out[-1].startswith("http") else None


def repo_path(page: Path) -> str:
    try:
        top = subprocess.run(["git", "-C", str(page.parent), "rev-parse", "--show-toplevel"], capture_output=True,
                             text=True).stdout.strip()
        if top:
            return page.resolve().relative_to(Path(top).resolve()).as_posix()
    except (OSError, ValueError):
        pass
    try:
        return page.resolve().relative_to(Path.cwd().resolve()).as_posix()
    except ValueError:
        return page.resolve().as_posix()


def main() -> None:
    args = sys.argv[1:]
    if not args or args[0].startswith("-"):
        sys.exit(__doc__)
    md = Path(args[0])
    if md.suffix != ".md" or not md.is_file():
        sys.exit(f"progress_link: no progress file {md}")
    md = md.resolve()
    count = args[args.index("--count") + 1] if "--count" in args else count_of(md)
    rebuild(md)
    page = md.with_suffix(".html")
    marker = md.parent / ".progress-desktop"
    desktop = "--desktop" in args or marker.exists()
    if "--desktop" in args and not marker.exists():
        try:
            marker.write_text("1\n")
        except OSError:
            pass
    base = start(md.parent) if desktop else running(md.parent)
    warn = bar_mismatch(md, count)
    if warn:
        print(warn, file=sys.stderr)
    if base:
        url = base + page.name
    else:
        url = repo_path(page)
        if " " in url or "(" in url or ")" in url:
            url = f"<{url}>"
    label = LABEL.get(md.name, md.stem)
    parts = [f"{label}: {count}" if count else label, f"[{page.name}]({url})"]
    print(" · ".join(parts))


if __name__ == "__main__":
    main()
