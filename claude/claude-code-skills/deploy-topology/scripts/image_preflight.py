#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Run on the built images what a platform team runs before accepting a service, so nothing new turns up there.

    python3 image_preflight.py contents <image>...
    python3 image_preflight.py stand [<project dir>] [--file docker-compose.test.yml] [--secret-free <image>]

  contents   needs no shell in the image: lists it with `docker export`. Checks the numeric non-root USER, the
             version in the environment, and that the app's own folders hold no compose file, .env*, Dockerfile,
             test, document, client source, key or working config (migrations are runtime and stay). In the static
             files of a client, no link to a public CDN.
  stand      brings the test compose file up as its own project under UID 5000 (read-only root, no capabilities —
             as the file already says) and checks: every app service starts; with the database stopped, liveness is
             200, readiness 503, a restarted backend stays up; the frontend starts with no backend and /metrics is
             not reachable through it; probes and scrapes leave no line in the backend's log; /metrics is Prometheus
             text; `docker stop` ends each app service with code 0. --secret-free <image> also runs the image with
             APP_ENV=prod and no secret: it must exit non-zero with a message. Takes the stand down at the end.

Exit 0 — clean; 1 — a line per problem; 2 — it could not run (no Docker, no compose file). Standard library only.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
import tarfile
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path

FOREIGN_UID = "5000:5000"
SKIP_TREES = ("node_modules/", ".venv/", "site-packages/", "/python/")
FORBIDDEN = [
    (re.compile(r"(^|/)docker-compose[^/]*\.ya?ml$"), "compose-файл"),
    (re.compile(r"(^|/)\.env(\.[^/]*)?$"), "файл переменных"),
    (re.compile(r"(^|/)Dockerfile[^/]*$|(^|/)\.dockerignore$"), "файл сборки"),
    (re.compile(r"(^|/)\.git(/|$)"), "папка .git"),
    (re.compile(r"\.(pem|key|crt|p12|pfx)$"), "ключ или сертификат"),
    (re.compile(r"(^|/)(tests?|__tests__)/|\.(test|spec)\.[cm]?[jt]sx?$|(^|/)test_[^/]*\.py$"), "тест"),
    (re.compile(r"(^|/)config\.(ya?ml|json|toml)$"), "рабочий конфиг"),
    (re.compile(r"\.(tsx|jsx)$"), "исходник фронта"),
    (re.compile(r"\.md$"), "документ"),
]
CDN = re.compile(r"https?://(fonts\.googleapis\.com|fonts\.gstatic\.com|cdnjs\.cloudflare\.com|cdn\.jsdelivr\.net|"
                 r"unpkg\.com|ajax\.googleapis\.com|code\.jquery\.com|cdn\.tailwindcss\.com)")
STATIC_DIRS = ("usr/share/nginx/html/", ".next/static/")


def run(cmd: list[str], timeout: int = 300) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)


def own_path(name: str, workdir: str) -> bool:
    """A path the project put there, not the base image's."""
    if any(skip in f"/{name}" for skip in SKIP_TREES):
        return False
    if name.startswith("usr/share/nginx/html/"):
        return True
    return bool(workdir) and name.startswith(workdir + "/")


def check_image(image: str, out: list[str]) -> None:
    info = run(["docker", "image", "inspect", image])
    if info.returncode != 0:
        out.append(f"{image}: образа нет локально")
        return
    config = json.loads(info.stdout)[0]["Config"]
    user = (config.get("User") or "").split(":")[0]
    if not user.isdigit() or user == "0":
        out.append(f"{image}: USER «{user or 'нет'}» — нужен числовой uid, не 0")
    env = dict(e.split("=", 1) for e in config.get("Env") or [] if "=" in e)
    if env.get("APP_VERSION", "dev") == "dev" or env.get("CI_COMMIT_SHORT_SHA", "unknown") == "unknown":
        out.append(f"{image}: в окружении образа нет APP_VERSION и CI_COMMIT_SHORT_SHA — соберите через build-images.sh")
    workdir = (config.get("WorkingDir") or "").strip("/")
    created = run(["docker", "create", image])
    if created.returncode != 0:
        out.append(f"{image}: docker create не прошёл: {created.stderr.strip()[-160:]}")
        return
    cid = created.stdout.strip()
    try:
        with tempfile.TemporaryFile() as tmp:
            subprocess.run(["docker", "export", cid], stdout=tmp, check=True)
            tmp.seek(0)
            with tarfile.open(fileobj=tmp) as tar:
                for member in tar:
                    name = member.name.lstrip("./")
                    if not member.isfile() or not own_path(name, workdir):
                        continue
                    relative = name[len(workdir) + 1:] if workdir and name.startswith(workdir + "/") else name
                    if relative.startswith("documentation/") and not relative.startswith("documentation/db/migrations/"):
                        out.append(f"{image}: /{name} — документация в образе")
                        continue
                    for pattern, what in FORBIDDEN:
                        if pattern.search(relative):
                            out.append(f"{image}: /{name} — {what} в образе")
                            break
                    if any(d in name for d in STATIC_DIRS) and name.endswith((".html", ".js", ".mjs", ".css")):
                        handle = tar.extractfile(member)
                        found = CDN.search((handle.read() if handle else b"").decode("utf-8", "replace"))
                        if found:
                            out.append(f"{image}: /{name} грузит {found.group(1)} — в закрытом контуре CDN недоступен")
    finally:
        run(["docker", "rm", "-f", cid])


def get(url: str, timeout: float = 4) -> tuple[int, str]:
    try:
        with urllib.request.urlopen(url, timeout=timeout) as answer:
            return answer.status, answer.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as error:
        return error.code, error.read().decode("utf-8", "replace")
    except OSError:
        return 0, ""


def wait_for(url: str, status: int, seconds: int = 40) -> bool:
    end = time.monotonic() + seconds
    while time.monotonic() < end:
        if get(url)[0] == status:
            return True
        time.sleep(1)
    return False


class Stand:
    def __init__(self, root: Path, file: str) -> None:
        self.root, self.file, self.project = root, file, f"{re.sub(r'[^a-z0-9]', '', root.name.lower())}-preflight"
        self.override: Path | None = None

    def compose(self, *args: str, timeout: int = 600) -> subprocess.CompletedProcess:
        cmd = ["docker", "compose", "--project-directory", str(self.root), "-p", self.project, "-f", self.file]
        if self.override:
            cmd += ["-f", str(self.override)]
        return run(cmd + list(args), timeout=timeout)

    def url(self, service: str, target: int, path: str) -> str | None:
        port = self.compose("port", service, str(target))
        if port.returncode != 0 or ":" not in port.stdout:
            return None
        return f"http://127.0.0.1:{port.stdout.strip().rsplit(':', 1)[1]}{path}"

    def container(self, service: str) -> str:
        return self.compose("ps", "-aq", service).stdout.strip().split("\n")[0]

    def running(self, service: str) -> bool:
        return run(["docker", "inspect", "--format", "{{.State.Running}}", self.container(service)]).stdout.strip() == "true"


def first_target(service: dict) -> int | None:
    ports = service.get("ports") or []
    return int(ports[0]["target"]) if ports else None


def check_stand(root: Path, file: str, secret_free: str | None, out: list[str]) -> None:
    stand = Stand(root, file)
    config = stand.compose("config", "--format", "json")
    if config.returncode != 0:
        out.append(f"{file}: compose не читается: {config.stderr.strip()[-200:]}")
        return
    services = json.loads(config.stdout)["services"]
    apps = [name for name, svc in services.items() if svc.get("build")]
    stores = [name for name, svc in services.items()
              if not svc.get("build") and re.search(r"postgres|mysql|mariadb", str(svc.get("image")), re.I)]
    if not apps:
        out.append(f"{file}: нет сервисов с build — проверять нечего")
        return
    with tempfile.NamedTemporaryFile("w", suffix=".yml", delete=False) as handle:
        handle.write("services:\n" + "".join(f"  {name}:\n    user: \"{FOREIGN_UID}\"\n" for name in apps))
    stand.override = Path(handle.name)
    try:
        up = stand.compose("up", "-d", "--wait", timeout=1200)  # the images up-test built, never a rebuild
        if up.returncode != 0:
            out.append(f"чужой UID: стенд под {FOREIGN_UID} не поднялся: {up.stderr.strip()[-300:]}")
            return
        print(f"  стенд поднят под UID {FOREIGN_UID}: {', '.join(apps)}")
        backend, frontend = services.get("backend"), services.get("frontend")
        target = first_target(backend) if backend else None
        base = stand.url("backend", target, "") if target else None
        if base:
            check_backend(stand, base, stores, out)
        else:
            print("  backend без опубликованного порта — проверки живости и логов пропущены")
        if frontend and backend:
            check_frontend(stand, first_target(frontend), out)
        for name in apps:
            if name == "migrate":
                continue
            stand.compose("stop", name)
            code = run(["docker", "inspect", "--format", "{{.State.ExitCode}}", stand.container(name)]).stdout.strip()
            if code != "0":
                out.append(f"остановка: {name} завершился с кодом {code}, нужен 0")
    finally:
        stand.compose("down", "-v", "--remove-orphans")
        stand.override.unlink(missing_ok=True)
    if secret_free:
        check_no_secrets(secret_free, out)


def check_backend(stand: Stand, base: str, stores: list[str], out: list[str]) -> None:
    if not wait_for(base + "/health/ready", 200):
        out.append("готовность: /health/ready не ответил 200 на поднятом стенде")
    status, body = get(base + "/metrics")
    if status != 200 or "# TYPE" not in body:
        out.append(f"метрики: /metrics ответил {status}, нет формата Prometheus")
    elif "app_build_info" not in body:
        out.append("метрики: нет app_build_info — версия сборки не видна")
    since = str(int(time.time()))
    for path in ("/health/live", "/health/ready", "/metrics"):
        for _ in range(3):
            get(base + path)
    time.sleep(1)
    logs = stand.compose("logs", "--no-color", "--no-log-prefix", "--since", since, "backend").stdout
    noisy = [line for line in logs.splitlines() if re.search(r"/health/(live|ready)|/metrics", line)]
    if noisy:
        out.append(f"шум проб: успешные обращения к служебным путям попали в лог ({len(noisy)} строк): {noisy[0][:120]}")
    if not stores:
        print("  нет базы в compose — проверка без базы пропущена")
        return
    stand.compose("stop", *stores)
    if not wait_for(base + "/health/ready", 503, 20):
        out.append("без базы: /health/ready не ответил 503")
    if get(base + "/health/live")[0] != 200:
        out.append("без базы: /health/live не 200 — сбой базы будет перезапускать поды по кругу")
    stand.compose("restart", "backend")
    time.sleep(5)
    if not stand.running("backend") or not wait_for(base + "/health/live", 200, 20):
        out.append("без базы: перезапущенный backend упал — нужна повторная попытка и готовность 503")
    stand.compose("start", *stores)
    if not wait_for(base + "/health/ready", 200, 40):
        out.append("база вернулась, а /health/ready не вернулся к 200")


def check_frontend(stand: Stand, target: int | None, out: list[str]) -> None:
    stand.compose("stop", "backend")
    stand.compose("restart", "frontend")
    time.sleep(4)
    if not stand.running("frontend"):
        logs = stand.compose("logs", "--no-color", "--tail", "3", "frontend").stdout.strip()[-200:]
        out.append(f"фронт без бэкенда не стартует — адрес ищется один раз при старте: {logs}")
    url = stand.url("frontend", target, "") if target else None
    if url:
        if not wait_for(url + "/", 200, 15):
            out.append("фронт без бэкенда: главная страница не отвечает 200")
        if "# TYPE" in get(url + "/metrics")[1]:
            out.append("метрики доступны через вход: /metrics фронта отдаёт Prometheus")
    stand.compose("start", "backend")


def check_no_secrets(image: str, out: list[str]) -> None:
    name = "image-preflight-no-secrets"
    run(["docker", "rm", "-f", name])
    started = run(["docker", "run", "-d", "--name", name, "--user", FOREIGN_UID, "--read-only", "--tmpfs", "/tmp",
                   "--cap-drop", "ALL", "--security-opt", "no-new-privileges", "-e", "APP_ENV=prod", image])
    if started.returncode != 0:
        out.append(f"без секретов: контейнер не создан: {started.stderr.strip()[-160:]}")
        return
    time.sleep(10)
    state = json.loads(run(["docker", "inspect", name]).stdout)[0]["State"]
    logs = run(["docker", "logs", name])
    run(["docker", "rm", "-f", name])
    if state["Running"] or state["ExitCode"] == 0:
        out.append(f"без секретов: {image} запустился с APP_ENV=prod и без обязательных переменных — должен отказать")
    elif not (logs.stdout + logs.stderr).strip():
        out.append(f"без секретов: {image} завершился без сообщения — назовите переменную")


def main() -> int:
    args = sys.argv[1:]
    if not args or args[0] not in ("contents", "stand"):
        print(__doc__)
        return 2
    if run(["docker", "version"]).returncode != 0:
        print("docker недоступен: проверка образа не выполнена")
        return 2
    out: list[str] = []
    if args[0] == "contents":
        images = [a for a in args[1:] if not a.startswith("--")]
        for image in images:
            check_image(image, out)
        title = f"образов {len(images)}"
    else:
        rest = args[1:]
        file = rest[rest.index("--file") + 1] if "--file" in rest else "docker-compose.test.yml"
        secret_free = rest[rest.index("--secret-free") + 1] if "--secret-free" in rest else None
        root = Path(next((a for a in rest if not a.startswith("--") and Path(a).is_dir()), ".")).resolve()
        if not (root / file).exists():
            print(f"{root / file}: файла нет")
            return 2
        check_stand(root, file, secret_free, out)
        title = "стенд"
    for line in out:
        print("✗", line)
    print(f"image_preflight: {title}, проблем {len(out)}")
    return 1 if out else 0


if __name__ == "__main__":
    sys.exit(main())
