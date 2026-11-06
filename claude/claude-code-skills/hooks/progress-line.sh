#!/bin/sh
# dev-pipeline: Stop — a turn that changed a progress file ends with the progress line, and the link is the page,
# never the .md (progress-line.py says why and how). Acts only where documentation/.dev-pipeline.json exists; without
# python3 it does nothing; never fails.
command -v python3 >/dev/null 2>&1 || { cat >/dev/null 2>&1; exit 0; }
python3 "$(dirname "$0")/progress-line.py" 2>/dev/null
exit 0
