"""Where the project stands, from the files and git only — the input of pipeline → «Where am I» and of `continue`.

    python3 where_am_i.py [<project dir>]

Prints, in Russian: the branch; the open iteration(s) — two open ones end in a request to ask which is current;
a resume note left by a stopped run (read it first); progress files with unfinished rows; each pipeline document
with its version, gates and pins (stale when a «ломает» row came after the pin); the plan's review, the
document-set check, the UI run and the audit with their verdicts; and, last, the open points in chain order. On a
fresh clone (no documentation/plans/) the closed iterations come from the tags v<version> and the units landed
since the last tag from the Plan-Unit: trailers; an iteration branch with no tag and no folder here (the current
one, or one on origin not merged into main) is the open iteration, with the open_iteration.py command to enter it.
A document committed on the iteration's branch but not stamped with its version marks its stage as still open
(pipeline → Commit each document as soon as it is written). Read-only. Python 3.9+, standard library only.
"""
from __future__ import annotations

import hashlib
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent.parent / "docs-consistency" / "scripts"))
try:
    import checked as dc_checked  # the document set and its hashes, shared with docs-consistency
except Exception:  # a broken neighbour must not break the answer
    dc_checked = None

PROGRESS = {  # file -> (stage, which statuses mean «not finished»)
    "progress-design.md": ("ui-design", "⏳🔄🔍🔁⛔"), "progress-screen-specs.md": ("screen-spec", "⏳🔄🔍🔁⛔"),
    "progress-test-cases.md": ("ui-test-cases write", "⏳🔄🔍🔁⛔"),
    "progress-architecture.md": ("clean-architecture-design", "⏳🔄🔍🔁⛔"),
    "progress-scaffold.md": ("repo-scaffold", "⏳🔄🔍🔁⛔"), "progress.md": ("work", "⏳🔄🔍🔁⛔"),
    "progress-deploy.md": ("deploy-topology", "⏳🔄🔍🔁⛔"),
    "test-run.md": ("ui-test-cases run", "⏳🔄"), "security-audit.md": ("security-audit", "⏳🔄🔍"),
}
STATUS_WORD = {"⏳": "ждут", "🔄": "в работе", "🔍": "на проверке", "🔁": "возвращены", "⛔": "остановлены"}
VERSION_RX = re.compile(r"\d+\.\d+\.\d+")


def git(root: Path, *args: str) -> str:
    try:
        r = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True, timeout=60)
    except (OSError, subprocess.TimeoutExpired):
        return ""
    return r.stdout.strip() if r.returncode == 0 else ""


def plan_units(root: Path, rng: str) -> list[str]:
    """Plan-Unit ids of the commits in rng, read from the message body: a Plan-Unit line that a blank line
    keeps out of git's trailer block still counts (work → references/run-hygiene.md → Commits)."""
    return re.findall(r"^Plan-Unit:\s*(\S+)\s*$", git(root, "log", rng, "--format=%B"), re.M)


def git_ok(root: Path, *args: str) -> bool:
    try:
        return subprocess.run(["git", "-C", str(root), *args], capture_output=True, timeout=60).returncode == 0
    except (OSError, subprocess.TimeoutExpired):
        return False


def vkey(v: str) -> tuple:
    """1.2.0 / 1.2 / v3 (the old numbers: doc-versioning → Moving from the old numbers) as a comparable tuple."""
    v = v.strip().strip('"\'')
    old = re.fullmatch(r"v(\d+)", v)
    nums = [int(x) for x in re.findall(r"\d+", v)] if not old else [int(old.group(1))]
    return tuple((nums + [0, 0, 0])[:3]) if not old else (-1, nums[0], 0)  # an old number precedes every release


def read(p: Path) -> str:
    try:
        return p.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def front(text: str) -> dict:
    """The frontmatter's scalar keys and its `sources:` list."""
    m = re.match(r"---\n(.*?)\n---", text, re.S)
    if not m:
        return {}
    meta: dict = {"sources": []}
    key = None
    for line in m.group(1).splitlines():
        kv = re.match(r"([A-Za-z_][\w-]*):\s*(.*)$", line)
        if kv:
            key = kv.group(1)
            if kv.group(2).strip():
                meta[key] = kv.group(2).strip().strip('"\'')
            continue
        item = re.match(r"\s+-\s+(.+)$", line)
        if item and key == "sources":
            meta["sources"].append(item.group(1).strip().strip('"\''))
    return meta


def openapi_info(text: str) -> dict:
    m = re.search(r"^info:\n((?:[ \t]+.*\n?|\n)*)", text, re.M)
    if not m:
        return {"sources": []}
    block = m.group(1)
    meta: dict = {"sources": []}
    for k, rk in (("version", "version"), ("x-reviewed", "reviewed")):
        mm = re.search(rf"^  {k}:\s*['\"]?([^'\"\n]+)", block, re.M)
        if mm:
            meta[rk] = mm.group(1).strip()
    src = re.search(r"^  x-sources:\n((?:    - .*\n?)+)", block, re.M)
    if src:
        meta["sources"] = [l.strip()[2:].strip().strip('"\'') for l in src.group(1).splitlines() if l.strip()]
    rows = []
    log = re.search(r"^  x-changelog:\n((?:    .*\n?)+)", block, re.M)
    if log:
        for item in re.split(r"^    - ", log.group(1), flags=re.M)[1:]:
            ver = re.search(r"version:\s*['\"]?([^'\"\n]+)", item)
            typ = re.search(r"type:\s*['\"]?([^'\"\n]+)", item)
            chg = re.search(r"change:\s*['\"]?([^'\"\n]+)", item)
            if ver:
                rows.append((ver.group(1).strip(), (typ.group(1) if typ else "").strip(), (chg.group(1) if chg else "").strip()))
    meta["rows"] = rows
    return meta


def journal(text: str) -> list:
    """The «Журнал изменений» rows as (version, type, change)."""
    m = re.search(r"^## Журнал изменений\s*\n(.*?)(?=^## |\Z)", text, re.M | re.S)
    rows = []
    for line in (m.group(1).splitlines() if m else []):
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) >= 4 and VERSION_RX.search(cells[0]) and not set(cells[0]) <= set("-: "):
            rows.append((cells[0], cells[3], cells[2]))
    return rows


class Doc:
    def __init__(self, root: Path, rel: str, label: str, stage: int, gate: str = ""):
        self.root, self.rel, self.label, self.stage, self.gate = root, rel, label, stage, gate
        self.path = root / rel
        text = read(self.path)
        if rel.endswith("openapi.yaml"):
            self.meta = openapi_info(text)
            self.rows = self.meta.get("rows", [])
        else:
            self.meta = front(text)
            self.rows = journal(text)


def registry(root: Path) -> list:
    """The pipeline's documents at their canonical paths (doc-versioning → Registry), in chain order."""
    d = "documentation/"
    docs = [
        Doc(root, d + "requirements/business-requirements/business-requirements.md", "бизнес-требования", 1, "grill"),
        Doc(root, d + "requirements/srs/srs.md", "SRS", 2, "srs"),
        Doc(root, d + "db/schema.md", "схема БД", 3, "review"),
        Doc(root, d + "api/openapi.yaml", "API (OpenAPI)", 4, "review"),
        Doc(root, d + "architecture/architecture.md", "архитектура — основа", 5, "review"),
        Doc(root, d + "architecture/domain.md", "доменная модель", 5, "review"),
    ]
    for p in sorted((root / d / "architecture/scenarios").glob("*/*.md")):
        docs.append(Doc(root, p.relative_to(root).as_posix(), f"сценарии {p.parent.name}/{p.stem}", 5, "review"))
    for p in sorted((root / d / "ui").glob("screen-specs/S-*.md")) + sorted((root / d / "ui").glob("*/screen-specs/S-*.md")):
        docs.append(Doc(root, p.relative_to(root).as_posix(), f"ТЗ на экран {p.stem.split('-')[0]}-{p.stem.split('-')[1]}"
                        if p.stem.count("-") else p.stem, 8, "review"))
    return docs


def pins(doc: Doc, by_path: dict) -> list:
    """One line per pin that is behind its source: stale (a «ломает» after it), behind («добавляет»), refresh."""
    out = []
    for src in doc.meta.get("sources", []):
        if "@" not in src:
            continue
        path, pin = src.rsplit("@", 1)
        source = by_path.get(path)
        if not source or not source.path.is_file() or "version" not in source.meta:
            continue
        cur = source.meta["version"]
        if vkey(pin) >= vkey(cur):
            continue
        after = [r for r in source.rows if vkey(r[0]) > vkey(pin)]
        types = {r[1] for r in after}
        if "ломает" in types:
            what = "; ".join(r[2][:70] for r in after if r[1] == "ломает")[:200]
            out.append(f"устарел: {Path(path).name}@{pin}, сейчас {cur} — ломает: {what}")
        elif "добавляет" in types:
            out.append(f"отстаёт: {Path(path).name}@{pin}, сейчас {cur} — только «добавляет» (дело сверки, этап 10)")
        else:
            out.append(f"пин обновится штампом: {Path(path).name}@{pin}, сейчас {cur} — только «уточняет»")
    return out


def srs_gates(root: Path) -> tuple:
    """The SRS's last stamp commit: (subject, grill, review, commits after it, uncommitted)."""
    log = git(root, "log", "--format=%H\t%s", "--", "documentation/requirements/srs/")
    for line in log.splitlines():
        sha, _, subj = line.partition("\t")
        if re.match(r"docs: SRS \d", subj):
            grill = re.search(r"grill:\s*([^·]+)", subj)
            review = re.search(r"review:\s*([^·]+)", subj)
            after = git(root, "log", "--oneline", f"{sha}..HEAD", "--", "documentation/requirements/srs/")
            dirty = git(root, "status", "--porcelain", "--", "documentation/requirements/srs/")
            return (subj, grill.group(1).strip() if grill else "в штампе не названо",
                    review.group(1).strip() if review else "в штампе не названо",
                    len(after.splitlines()) if after else 0, bool(dirty))
    return None


def progress(folder: Path) -> list:
    out = []
    for name, (stage, unfinished) in PROGRESS.items():
        p = folder / name
        text = read(p)
        if not text:
            continue
        rows = [l for l in text.splitlines() if l.startswith("|") and not re.match(r"\|\s*-", l)]
        counts = {s: sum(1 for l in rows if s in l) for s in unfinished}
        left = {s: n for s, n in counts.items() if n}
        bar = re.search(r"[█░]{5,}[^\n]*?(\d{1,3})\s*%", text)
        count = re.search(r"^[^|#\n]{0,40}?(\d+\s*из\s*\d+[^\n]*)$", text, re.M)
        verdict = re.search(r"^Verdict:\s*(\S+)", text, re.M)
        state = (count.group(1).strip() if count else (bar.group(1) + "%" if bar else ""))
        tail = ", ".join(f"{STATUS_WORD[s]} {n}" for s, n in left.items())
        out.append((name, stage, state, tail, verdict.group(1) if verdict else "", bool(left)))
    return out


def iterations(plans: Path) -> tuple:
    if not plans.is_dir():
        return [], []
    vs = sorted((p for p in plans.iterdir() if p.is_dir() and re.fullmatch(r"\d+\.\d+\.\d+", p.name)),
                key=lambda p: vkey(p.name))
    return [p.name for p in vs if not (p / "summary.md").exists()], [p.name for p in vs if (p / "summary.md").exists()]


def main_ref(root: Path) -> str | None:
    return next((b for b in ("origin/main", "main", "origin/master", "master")
                 if git_ok(root, "rev-parse", "-q", "--verify", b)), None)


def branch_iterations(root: Path, branch: str, closed: list) -> list:
    """Open iterations named only by a branch, with no plans/ folder here (a fresh clone, or another person's pushed
    work): [(version, ref)] — the current branch alone when it is one, else every iteration branch here or on origin
    whose version has no tag and is not merged into main."""
    done = set(closed) | {t[1:] for t in git(root, "tag", "--list", "v*").split()}
    m = re.match(r"iteration/(\d+\.\d+\.\d+)$", branch)
    if m:
        return [] if m.group(1) in done else [(m.group(1), branch)]
    into = main_ref(root)
    found: dict = {}
    for ref in git(root, "for-each-ref", "--format=%(refname:short)", "refs/heads/iteration/",
                   "refs/remotes/origin/iteration/").split():
        v = ref.rsplit("/", 1)[-1]
        if VERSION_RX.fullmatch(v) and v not in done and v not in found and not (
                into and git_ok(root, "merge-base", "--is-ancestor", ref, into)):
            found[v] = ref
    return sorted(found.items(), key=lambda kv: vkey(kv[0]))


DOC_FILES = {"documentation/requirements/srs/srs.md": "documentation/requirements/srs",
             "documentation/db/schema.md": "documentation/db", "documentation/api/openapi.yaml": "documentation/api"}
NOT_A_STAGE_COMMIT = re.compile(r"^docs: решение изменено|\(плагин \d")


def unstamped(root: Path, doc: Doc, version: str | None) -> bool:
    """Written or changed on this iteration's branch by its stage, and not stamped with the iteration's version yet:
    the stage is still open (its gates and its stamp). Decision changes and plugin-format commits do not count."""
    if not version or doc.meta.get("version") == version or not doc.path.is_file():
        return False
    into = main_ref(root)
    base = git(root, "merge-base", "HEAD", into) if into else ""
    span = f"{base}..HEAD" if base else "HEAD"
    subjects = git(root, "log", "--format=%s", span, "--", DOC_FILES.get(doc.rel, doc.rel)).splitlines()
    return any(s and not NOT_A_STAGE_COMMIT.search(s) for s in subjects)


def plan_state(folder: Path) -> list:
    out, opens = [], []
    plan, review = folder / "plan.md", folder / "plan-review.md"
    if plan.is_file():
        line = "план: plan.md"
        if not review.is_file():
            line += " · plan-review: не запускался"
            opens.append("ревью плана (plan-review) не запускалось — `plan` запускает его сам")
        else:
            head = read(review).splitlines()[:3]
            verdict = next((l.split(":", 1)[1].strip() for l in head if l.startswith("Verdict:")), "нет строки Verdict")
            line += f" · plan-review: {verdict}"
            chk = next((l.split(":", 1)[1].strip() for l in head if l.startswith("checked:")), None)
            if chk:
                now = hashlib.sha256(plan.read_bytes()).hexdigest()
                if not (now.startswith(chk) or chk.startswith(now)):
                    line += " · план изменён после проверки"
                    opens.append("план изменён после plan-review — проверить заново до work")
            if not verdict.startswith("PASS"):
                opens.append(f"plan-review: {verdict} — план не прошёл проверку")
        out.append(line)
    return out, opens


def consistency(root: Path, folder: Path) -> tuple:
    rep = folder / "docs-consistency.md"
    if not rep.is_file():
        return "сверка (docs-consistency): не запускалась в этой итерации", None
    verdict = (read(rep).splitlines() or [""])[0].replace("Verdict:", "").strip() or "нет строки Verdict"
    line = f"сверка (docs-consistency): {verdict}"
    if dc_checked is not None:
        moved = dc_checked.diff(root, rep)
        if moved:
            kinds = {}
            for k, p in moved:
                kinds.setdefault(k, []).append(Path(p).name)
            word = {"changed": "изменены", "gone": "удалены", "new": "не проверялись (новые)"}
            line += " · после сверки: " + "; ".join(f"{word[k]} {', '.join(v[:4])}{' …' if len(v) > 4 else ''}"
                                                    for k, v in kinds.items())
            return line, "сверка устарела: документы изменились после неё — этап 10 заново"
        line += " · документы с тех пор не менялись"
    return line, None if verdict.startswith("PASS") else f"сверка: {verdict}"


def main() -> None:
    given = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    top = git(given, "rev-parse", "--show-toplevel")
    # a system in a subfolder of a bigger repository keeps its own documentation/ (doc-versioning → monorepo)
    root = given if (given / "documentation").is_dir() or not top else Path(top)
    doc = root / "documentation"
    plans = doc / "plans"
    print(f"Проект: {root}")
    branch = git(root, "symbolic-ref", "-q", "--short", "HEAD") or "(не git или detached HEAD)"
    dirty = git(root, "status", "--porcelain", "--", ".")
    print(f"Ветка: {branch} · незакоммичено: {len(dirty.splitlines()) if dirty else 'ничего'}")
    opens: list = []

    open_, closed = iterations(plans)
    by_branch = [] if open_ else branch_iterations(root, branch, closed)
    if open_:
        print(f"Итерации: открыта {', '.join(open_)}" + (f"; закрыты {', '.join(closed)}" if closed else ""))
        if len(open_) > 1:
            print(f"!! Открыто итераций: {len(open_)} ({', '.join(open_)}). Спросите пользователя, какую продолжаем, "
                  "прежде чем что-то штамповать или коммитить (одним вопросом).")
    elif by_branch:
        for v, ref in by_branch:
            print(f"Итерация {v} открыта по ветке {ref}: папки documentation/plans/{v}/ здесь нет (свежий клон "
                  "или работа другого человека)")
        if len(by_branch) > 1:
            print(f"!! Открытых веток итераций: {len(by_branch)}. Спросите пользователя, какую продолжаем (одним "
                  "вопросом).")
        v = by_branch[0][0]
        print(f"  войти: python3 \"{HERE / 'open_iteration.py'}\" {v} — переключит на ветку и создаст папку; номер "
              "версии не спрашивать")
        print("  этапы 10–14 по файлам здесь не видны: их отчёты лежат в plans/ на машине, где шли (в git не хранятся)")
        opens.append(f"войти в итерацию {v} (ветка {by_branch[0][1]}): open_iteration.py {v}")
    elif closed:
        print(f"Итерации: открытых нет; закрыты {', '.join(closed)} — следующая откроется первым этапом "
              "(open_iteration.py)")
    else:
        tags = sorted((t for t in git(root, "tag", "--list", "v*").split() if VERSION_RX.fullmatch(t[1:])),
                      key=lambda t: vkey(t[1:]))
        since = f"{tags[-1]}..HEAD" if tags else "HEAD"
        units = plan_units(root, since)
        print("Итерации: documentation/plans/ нет (свежий клон или проект до первой итерации)")
        print(f"  теги: {', '.join(tags) if tags else 'нет'} · задач с Plan-Unit после "
              f"{tags[-1] if tags else 'начала'}: {len(set(units))}" + (f" ({', '.join(sorted(set(units))[:8])}"
                                                                         f"{' …' if len(set(units)) > 8 else ''})" if units else ""))
    cur = open_[-1] if open_ else None
    it_version = cur or (by_branch[0][0] if by_branch else None)
    folder = plans / cur if cur else None

    if folder and (folder / "resume.md").is_file():
        upd = re.search(r"Обновлено:\s*([^·\n]+)", read(folder / "resume.md"))
        print(f"Прерванный прогон: documentation/plans/{cur}/resume.md" + (f" (обновлено {upd.group(1).strip()})" if upd else "")
              + " — прочитать первым и сверить с git (pipeline → references/pause-and-resume.md)")
        opens.append(f"прерванный прогон — продолжить по documentation/plans/{cur}/resume.md")

    if folder:
        rows = progress(folder)
        if rows:
            print("Файлы прогресса:")
        for name, stage, state, tail, verdict, unfinished in rows:
            print(f"  {name} ({stage}): {state}" + (f" · {tail}" if tail else "") + (f" · Verdict: {verdict}" if verdict else ""))
            if unfinished:
                opens.append(f"{stage} не закончен ({name}: {tail})")

    docs = registry(root)
    by_path = {d.rel: d for d in docs}
    open_stages: dict = {}
    print("Документы:")
    for d in docs:
        if not d.path.is_file():
            if d.stage <= 5 and "scenarios" not in d.rel:
                print(f"  {d.stage}. {d.label}: нет")
            continue
        meta, bits = d.meta, []
        if meta.get("version"):
            bits.append(meta["version"])
        if d.gate == "grill":
            g, u = meta.get("grilled"), meta.get("updated")
            if not g:
                bits.append("допрос: не запускался")
                opens.append("допрос бизнес-требований (grill-me) не запускался")
            elif u and u > g:
                bits.append(f"допрос {g}, документ изменён {u} — допрос не по текущему тексту")
                opens.append("бизнес-требования изменены после допроса")
            else:
                bits.append(f"допрос {g}")
        elif d.gate == "srs":
            st = srs_gates(root)
            if st is None:
                bits.append("штампа нет (ворота не записаны)")
                opens.append("SRS без штампа: допрос и ревью не записаны — спросить о допросе")
            else:
                subj, grill, review, after, dirty_srs = st
                bits.append(f"допрос: {grill} · ревью: {review}")
                if after or dirty_srs:
                    bits.append("после штампа: " + ", ".join(x for x in (f"коммитов {after}" if after else "",
                                                                          "есть незакоммиченное" if dirty_srs else "") if x))
                for gate, val in (("допрос SRS", grill), ("ревью SRS", review)):
                    if val.startswith("не запускался") or val == "в штампе не названо":
                        opens.append(f"{gate}: {val}")
        elif d.gate == "review":
            bits.append(f"ревью: {meta['reviewed']}" if meta.get("reviewed") else "ревью: нет отметки (пропущено или не запускалось)")
        draft = d.gate == "review" and unstamped(root, d, it_version)
        for p in pins(d, by_path):
            bits.append(p)
            if p.startswith("устарел") and not draft:  # a draft of this iteration gets its pins with the stamp
                opens.append(f"устарел документ «{d.label}» — этап {d.stage} обновляет его по журналу источника")
        if draft:
            bits.append(f"написан в итерации {it_version}, этап не закрыт (нет отметки версии)")
            open_stages.setdefault(d.stage, []).append(d.label)
        print(f"  {d.stage}. {d.label}: " + " · ".join(bits))
    for stage, labels in open_stages.items():
        opens.append(f"этап {stage} не закрыт: {', '.join(labels[:4])}{' …' if len(labels) > 4 else ''} — написаны и "
                     "закоммичены, проверка и отметка версии не сделаны")
    ui = sorted(doc.glob("ui/frames-register.md")) + sorted(doc.glob("ui/*/frames-register.md"))
    for reg in ui:
        owner = re.search(r"Дизайн ведёт:?\**:?\s*([^\n|]+)", read(reg))
        print(f"  7. макеты: {reg.relative_to(root)}" + (f" · дизайн ведёт: {owner.group(1).strip(' *`')}" if owner else ""))
    tc = sorted(doc.glob("ui/test-cases/README.md")) + sorted(doc.glob("ui/*/test-cases/README.md"))
    for t in tc:
        print(f"  9. тест-кейсы: {t.parent.relative_to(root)}")
    extra = [("6. каркас — карта проекта", doc / "project-map/project-map.md"),
             ("15. развёртывание", doc / "deploy/deploy.md"), ("16. эксплуатация", doc / "operations/operations.md")]
    for label, p in extra:
        if p.is_file():
            print(f"  {label}: {p.relative_to(root)}")
    ci = sorted((root / ".github/workflows").glob("*.y*ml")) if (root / ".github/workflows").is_dir() else []
    if ci:
        print(f"  17. CI: {', '.join(c.name for c in ci)}")

    if folder:
        print(f"Итерация {cur}:")
        line, issue = consistency(root, folder)
        print(f"  10. {line}")
        if issue and (folder / "docs-consistency.md").is_file():
            opens.append(issue)
        lines, plan_opens = plan_state(folder)
        for l in lines:
            print(f"  11. {l}")
        opens += plan_opens
        base = "main" if git(root, "rev-parse", "-q", "--verify", "main") else "master"
        units = plan_units(root, f"{base}..HEAD")
        if units:
            print(f"  12. задач с Plan-Unit на ветке: {len(set(units))}")
        for name, label, n in (("test-run.md", "проверка через интерфейс", 13), ("security-audit.md", "аудит безопасности", 14)):
            v = re.search(r"^Verdict:\s*(\S+)", read(folder / name), re.M)
            if v:
                print(f"  {n}. {label}: {v.group(1)}")
                if v.group(1) in ("DEFECTS", "FIX"):
                    opens.append(f"{label}: {v.group(1)} — план исправлений (plan, MODE fix)")

    print("Открытые пункты (по порядку):" if opens else "Открытых пунктов по файлам нет — следующий этап по таблице pipeline.")
    for o in dict.fromkeys(opens):
        print(f"  - {o}")


if __name__ == "__main__":
    main()
