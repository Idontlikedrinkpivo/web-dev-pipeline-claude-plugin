#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Is Shannon ready to run against the local test stand — security-audit's optional live check
(references/live-pentest.md).

    python3 shannon_check.py --url http://127.0.0.1:8080 [--no-docker-reach]

One line each, ✅ or ✗:
  docker       the Docker daemon answers (Shannon's worker is a container);
  node         Node.js 18 or newer and npx (Shannon runs through `npx @keygraph/shannon`);
  credentials  a key or a sign-in Shannon can use — ~/.shannon/config.toml (its setup wizard), a provider's key
               variable, or SHANNON_USE_PI_AUTH=1 with ~/.pi/agent/auth.json (a ChatGPT Plus/Pro or xAI
               subscription) — only whether one is there, never its value;
  stand        the stand answers at --url, and from a container at host.docker.internal on the same port (Docker
               cannot reach the host's 127.0.0.1) — skipped with --no-docker-reach.
Exit 0 — ready, with the -u address to give Shannon; 2 — something missing (the lines say what); 3 — --url is not a
local stand: Shannon changes data, so a server, staging or prod address is refused. Standard library only.
"""
from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

LOCAL = {"127.0.0.1", "localhost", "::1", "host.docker.internal"}
KEYS = ("ANTHROPIC_API_KEY", "OPENAI_API_KEY", "XAI_API_KEY", "OPENROUTER_API_KEY", "AWS_BEARER_TOKEN_BEDROCK")


def run(*cmd: str, timeout: int = 60) -> tuple[int, str]:
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return p.returncode, (p.stdout or "").strip()
    except (OSError, subprocess.TimeoutExpired):
        return 1, ""


def answers(url: str) -> bool:
    try:
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        with opener.open(url, timeout=5) as r:
            return r.status < 500
    except urllib.error.HTTPError as e:
        return e.code < 500
    except (urllib.error.URLError, OSError, ValueError):
        return False


def main() -> None:
    args = sys.argv[1:]
    url = args[args.index("--url") + 1] if "--url" in args else "http://127.0.0.1:8080"
    host = urllib.parse.urlparse(url).hostname or ""
    if host not in LOCAL:
        print(f"✗ стенд: {url} — не локальный адрес. Shannon меняет данные: только локальный тестовый стенд, "
              "не сервер, не staging, не прод")
        sys.exit(3)
    port = urllib.parse.urlparse(url).port or 80
    rows: list[tuple[bool, str]] = []

    code, _ = run("docker", "info", timeout=20)
    rows.append((code == 0, "docker: работает" if code == 0 else "docker: не отвечает — запустите Docker Desktop"))

    code, out = run("node", "--version")
    major = int(m.group(1)) if code == 0 and (m := re.match(r"v(\d+)", out)) else 0
    npx = shutil.which("npx") is not None
    rows.append((major >= 18 and npx, f"node: {out or 'нет'}" + ("" if major >= 18 and npx else
                                                                  " — нужен Node.js 18 или новее с npx")))

    home = Path.home()
    sources = []
    if (home / ".shannon" / "config.toml").exists():
        sources.append("~/.shannon/config.toml")
    sources += [k for k in KEYS if os.environ.get(k)]
    if os.environ.get("SHANNON_USE_PI_AUTH") == "1" and (home / ".pi" / "agent" / "auth.json").exists():
        sources.append("вход по подписке (Pi)")
    rows.append((bool(sources), "ключ или вход: " + (", ".join(sources) if sources else
                 "нет — `npx @keygraph/shannon@latest setup` или вход по подписке (references/live-pentest.md → 3)")))

    up = answers(url)
    target = f"{urllib.parse.urlparse(url).scheme}://host.docker.internal:{port}"
    reach = True
    if up and "--no-docker-reach" not in args and rows[0][0]:
        code, out = run("docker", "run", "--rm", "--add-host=host.docker.internal:host-gateway", "curlimages/curl:8.11.1",
                        "-s", "-o", "/dev/null", "-w", "%{http_code}", "--max-time", "5", f"{target}/", timeout=120)
        reach = code == 0 and out[:1] in "1234" and out != "000"
    rows.append((up and reach, f"стенд: {url} " + ("отвечает" if up else "не отвечает — поднимите его по verify-скилу")
                 + ("" if not up else f"; из контейнера {target} " + ("доступен" if reach else "недоступен"))))

    for ok, line in rows:
        print(("✅ " if ok else "✗ ") + line)
    if all(ok for ok, _ in rows):
        print(f"shannon_check: готово к запуску — -u {target}")
        sys.exit(0)
    print("shannon_check: не готово — " + "; ".join(line.split(" — ")[0] for ok, line in rows if not ok))
    sys.exit(2)


if __name__ == "__main__":
    main()
