#!/bin/sh
# dev-pipeline: PreCompact — in the session running work, an automatic compaction waits until no unit is in flight;
# every compaction in a pipeline project gets what its summary must keep (compact-hold.py says why and how). Acts only
# in a pipeline project (stamp or documentation/plans/); without python3 it does nothing; never fails.
command -v python3 >/dev/null 2>&1 || { cat >/dev/null 2>&1; exit 0; }
python3 "$(dirname "$0")/compact-hold.py" 2>/dev/null
exit 0
