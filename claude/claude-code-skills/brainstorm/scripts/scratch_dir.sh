#!/usr/bin/env bash
# This brainstorm run's private scratch folder — where the grounding dossier is saved so a compaction does not lose
# it. Creates it and prints its absolute path.
#
#     bash scratch_dir.sh <run-slug>        # → /tmp/brainstorm-<uid>/brainstorm/<run-slug>
#
# The root is per user, mode 700, and refused when it is a symlink or owned by someone else: another account on the
# machine must not plant files into the dossier or read it. Exit 0 — the path printed; 1 — an unsafe root; 2 — a bad
# slug (letters, digits, dot, dash, underscore; not starting with a dot).
set -u
slug="${1:-}"
case "$slug" in
  "" | .* | *[!A-Za-z0-9._-]*) echo "usage: scratch_dir.sh <run-slug> (letters, digits, . _ -)" >&2; exit 2 ;;
esac
root="/tmp/brainstorm-$(id -u)"
if [ -L "$root" ]; then echo "unsafe scratch root symlink: $root" >&2; exit 1; fi
(umask 077; mkdir -p "$root") || exit 1
if [ -L "$root" ] || [ ! -O "$root" ]; then echo "scratch root is not owned by the current user: $root" >&2; exit 1; fi
chmod 700 "$root" || exit 1
dir="$root/brainstorm/$slug"
(umask 077; mkdir -p "$dir") || exit 1
chmod 700 "$dir" || exit 1
echo "$dir"
