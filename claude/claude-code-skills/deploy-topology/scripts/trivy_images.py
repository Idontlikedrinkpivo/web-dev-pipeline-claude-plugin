#!/usr/bin/env python3
"""Scan every image of a release tar with trivy, one JSON file per image.

Usage: trivy_images.py <release tar> <out dir> [--severity HIGH,CRITICAL]

`trivy image --input` takes a single-image archive; on the release tar
(backend + frontend in one file) it prints nothing and exits 0. So the image
names are read from manifest.json, loaded into docker if missing, and scanned
by name through the docker socket. An empty or malformed report is a failed
scan, never "0 findings". Vulnerabilities are filtered by --severity; a secret
counts at any severity. Exit 0: every image scanned, nothing that stops the
hand-over; 2: scanned, and a CRITICAL or a secret was found; 1: a scan failed.
"""
import json
import re
import subprocess
import sys
import tarfile
from pathlib import Path


def image_names(tar_path):
    with tarfile.open(tar_path) as tar:
        member = tar.extractfile("manifest.json")
        manifest = json.load(member)
    return [t for entry in manifest for t in (entry.get("RepoTags") or [])]


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)


def trivy(name, *options):
    """Return (report dict, None) or (None, reason)."""
    cmd = ["docker", "run", "--rm", "-v", "/var/run/docker.sock:/var/run/docker.sock",
           "-v", "pipeline-trivy-cache:/root/.cache/trivy", "aquasec/trivy:latest",
           "image", name, "--format", "json", *options]
    res = run(cmd)
    if not res.stdout.strip():
        return None, "пустой вывод trivy (%s)" % (res.stderr.strip()[-200:] or "без сообщения")
    try:
        report = json.loads(res.stdout)
    except ValueError:
        return None, "вывод trivy не JSON"
    if not isinstance(report, dict) or "Results" not in report:
        return None, "в отчёте нет ключа Results"
    return report, None


def scan(name, severity):
    """Vulnerabilities at the given severity and secrets at any, as one report."""
    report, why = trivy(name, "--scanners", "vuln", "--severity", severity)
    if report is None:
        return None, why
    secrets, why = trivy(name, "--scanners", "secret")
    if secrets is None:
        return None, why
    report["Results"] = (report["Results"] or []) + (secrets["Results"] or [])
    return report, None


def main(argv):
    args = [a for a in argv if not a.startswith("--severity")]
    severity = "HIGH,CRITICAL"
    if "--severity" in argv:
        severity = argv[argv.index("--severity") + 1]
        args = [a for a in args if a != severity]
    if len(args) != 2:
        print("Использование: trivy_images.py <tar релиза> <папка вывода> [--severity HIGH,CRITICAL]")
        return 1
    tar_path, out_dir = args
    try:
        names = image_names(tar_path)
    except (OSError, KeyError, ValueError, tarfile.TarError) as exc:
        print("Не удалось прочитать manifest.json из %s: %s" % (tar_path, exc))
        return 1
    if not names:
        print("В manifest.json нет ни одного образа (RepoTags пуст): %s" % tar_path)
        return 1
    try:
        Path(out_dir).mkdir(parents=True, exist_ok=True)
        loaded = False
        failed = 0
        total = {"HIGH": 0, "CRITICAL": 0, "SECRET": 0}
        for name in names:
            if run(["docker", "image", "inspect", name]).returncode != 0 and not loaded:
                loaded = True
                load = run(["docker", "load", "-i", tar_path])
                if load.returncode != 0:
                    print("docker load не удался: %s" % (load.stderr.strip()[-200:] or "без сообщения"))
            report, why = scan(name, severity)
            if report is None:
                failed += 1
                print("trivy %s: СКАН НЕ УДАЛСЯ — %s" % (name, why))
                continue
            counts = {"HIGH": 0, "CRITICAL": 0, "SECRET": 0}
            for result in report["Results"] or []:
                for vuln in result.get("Vulnerabilities") or []:
                    if vuln.get("Severity") in counts:
                        counts[vuln["Severity"]] += 1
                counts["SECRET"] += len(result.get("Secrets") or [])
            out = Path(out_dir) / ("trivy-%s.json" % re.sub(r"[/:]", "_", name))
            out.write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
            for key in total:
                total[key] += counts[key]
            print("trivy %s: HIGH %d · CRITICAL %d · секретов %d → %s"
                  % (name, counts["HIGH"], counts["CRITICAL"], counts["SECRET"], out))
    except FileNotFoundError:
        print("docker не найден: образы нельзя проверить, скан не выполнен")
        return 1
    code = 1 if failed else 2 if total["CRITICAL"] or total["SECRET"] else 0
    verdict = {0: "все образы просканированы", 1: "есть неудавшиеся сканы, это не «0 находок»",
               2: "CRITICAL или секрет — комплект не передаётся (images.md → What stops the hand-over)"}[code]
    print("Итого: образов %d, просканировано %d, HIGH %d · CRITICAL %d · секретов %d. Код выхода %d: %s"
          % (len(names), len(names) - failed, total["HIGH"], total["CRITICAL"], total["SECRET"], code, verdict))
    return code


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
