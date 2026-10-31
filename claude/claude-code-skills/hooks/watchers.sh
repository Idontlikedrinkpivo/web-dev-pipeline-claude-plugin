#!/bin/sh
# dev-pipeline: SubagentStop — an agent may not end while a background task it started still runs (watchers.py says
# why and how). Acts only where documentation/.dev-pipeline.json exists; without python3 it does nothing; never fails.
command -v python3 >/dev/null 2>&1 || { cat >/dev/null 2>&1; exit 0; }
python3 "$(dirname "$0")/watchers.py" 2>/dev/null
exit 0
