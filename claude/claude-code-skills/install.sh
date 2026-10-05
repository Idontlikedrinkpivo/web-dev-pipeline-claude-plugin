#!/usr/bin/env bash
# ALTERNATIVE INSTALL — only for a setup that cannot use the dev-pipeline plugin.
# Do not combine with the plugin: the same skills would exist twice (`work` and
# `dev-pipeline:work`) and drift apart. Prefer:
#   claude plugin install dev-pipeline@dev-pipeline-marketplace
#
# Links this skills folder into Claude Code:
#   _agents/*.md          -> ~/.claude/agents/<name>.md   (one agent per executor-catalog row)
#   <skill>/ with SKILL.md -> ~/.claude/skills/<skill>    (except the names in DRAFTS)
#
#   bash install.sh              install or refresh the links (safe to re-run)
#   bash install.sh --uninstall  remove only the links that point into this folder
#
# Never overwrites a real file or folder: a target that exists and is not a
# symlink is reported and skipped. A symlink is replaced only when it points
# somewhere else. CLAUDE_CONFIG_DIR is honoured when set.

# Skill folders that are not ready to share. Space-separated folder names.
DRAFTS=""

set -u
set -o pipefail
shopt -s nullglob

usage() {
  sed -n '2,11p' "$0" | sed 's/^# \{0,1\}//'
}

MODE="install"
case "${1:-}" in
  "") ;;
  --uninstall) MODE="uninstall" ;;
  -h|--help) usage; exit 0 ;;
  *) printf 'Unknown argument: %s\n\n' "$1" >&2; usage >&2; exit 2 ;;
esac
if [ "$#" -gt 1 ]; then
  printf 'Too many arguments.\n\n' >&2; usage >&2; exit 2
fi

ROOT="$(cd -P "$(dirname "$0")" && pwd -P)" || { echo "Cannot resolve the script folder." >&2; exit 1; }
CLAUDE_DIR="${CLAUDE_CONFIG_DIR:-$HOME/.claude}"
AGENTS_DIR="$CLAUDE_DIR/agents"
SKILLS_DIR="$CLAUDE_DIR/skills"

linked=0; kept=0; relinked=0; skipped=0; removed=0; failed=0
WARNINGS=""

warn() {
  printf 'WARN  %s\n' "$1" >&2
  WARNINGS="${WARNINGS}  - $1
"
}

# Physical absolute path of $1, following symlinks on the last component.
# Prints nothing and returns 1 when the parent folder does not exist.
physical() {
  local p="$1" link dir n=0
  while [ -L "$p" ]; do
    n=$((n + 1))
    [ "$n" -gt 40 ] && return 1
    link="$(readlink "$p")" || return 1
    case "$link" in
      /*) p="$link" ;;
      *) p="$(dirname "$p")/$link" ;;
    esac
  done
  dir="$(cd -P "$(dirname "$p")" 2>/dev/null && pwd -P)" || return 1
  printf '%s/%s\n' "$dir" "$(basename "$p")"
}

# True when the symlink $1 points into this folder (resolved or dangling).
points_here() {
  local raw resolved
  raw="$(readlink "$1")" || return 1
  case "$raw" in "$ROOT"/*) return 0 ;; esac
  resolved="$(physical "$1")" || return 1
  case "$resolved" in "$ROOT"/*) return 0 ;; esac
  return 1
}

is_draft() {
  case " $DRAFTS " in *" $1 "*) return 0 ;; esac
  return 1
}

# link SRC DST — create or refresh one symlink, never touching a real file.
link() {
  local src="$1" dst="$2" current
  if [ -L "$dst" ]; then
    if [ "$(physical "$dst")" = "$(physical "$src")" ]; then
      kept=$((kept + 1))
      return 0
    fi
    current="$(readlink "$dst")"
    if rm "$dst" && ln -s "$src" "$dst"; then
      printf 'RELINK %s (was -> %s)\n' "$dst" "$current"
      relinked=$((relinked + 1))
    else
      warn "could not relink $dst"
      failed=$((failed + 1))
    fi
  elif [ -e "$dst" ]; then
    warn "$dst exists and is not a symlink — skipped, move it away to install this one"
    skipped=$((skipped + 1))
  else
    if ln -s "$src" "$dst"; then
      printf 'LINK  %s\n' "$dst"
      linked=$((linked + 1))
    else
      warn "could not link $dst"
      failed=$((failed + 1))
    fi
  fi
}

# prune DIR — remove dangling symlinks in DIR that point into this folder
# (an agent or skill that was deleted or renamed here).
prune() {
  local entry
  for entry in "$1"/*; do
    if [ -L "$entry" ] && [ ! -e "$entry" ] && points_here "$entry"; then
      if rm "$entry"; then
        printf 'PRUNE %s (target is gone)\n' "$entry"
        removed=$((removed + 1))
      else
        warn "could not remove dangling $entry"
        failed=$((failed + 1))
      fi
    fi
  done
}

install_all() {
  local file name skill_dir skill
  if ! mkdir -p "$AGENTS_DIR" "$SKILLS_DIR"; then
    echo "Cannot create $AGENTS_DIR or $SKILLS_DIR." >&2
    exit 1
  fi

  echo "Agents -> $AGENTS_DIR"
  for file in "$ROOT"/_agents/*.md; do
    name="$(basename "$file" .md)"
    [ "$name" = "README" ] && continue
    if ! grep -q "^name: $name\$" "$file"; then
      warn "_agents/$name.md: frontmatter name is not '$name' — Claude Code will not find it as subagent_type \"$name\""
    fi
    if [ -f "$ROOT/.claude-plugin/plugin.json" ] && ! grep -q "\"./_agents/$name.md\"" "$ROOT/.claude-plugin/plugin.json"; then
      warn "_agents/$name.md is not listed in .claude-plugin/plugin.json — the plugin will not load it"
    fi
    link "$file" "$AGENTS_DIR/$name.md"
  done
  prune "$AGENTS_DIR"

  echo "Skills -> $SKILLS_DIR"
  for skill_dir in "$ROOT"/*/; do
    skill_dir="${skill_dir%/}"
    skill="$(basename "$skill_dir")"
    case "$skill" in _*|.*) continue ;; esac
    [ -f "$skill_dir/SKILL.md" ] || continue
    if is_draft "$skill"; then
      if [ -L "$SKILLS_DIR/$skill" ] && points_here "$SKILLS_DIR/$skill"; then
        warn "draft '$skill' is still linked at $SKILLS_DIR/$skill — remove that link if it should not load"
      fi
      printf 'DRAFT %s (not linked)\n' "$skill"
      continue
    fi
    link "$skill_dir" "$SKILLS_DIR/$skill"
  done
  prune "$SKILLS_DIR"

  echo
  echo "Summary: $linked linked, $relinked relinked, $kept already in place, $removed pruned, $skipped skipped, $failed failed."
  echo "Drafts not installed: ${DRAFTS:-none}"
  echo "Restart Claude Code so it loads new or changed agents and skills."
}

uninstall_all() {
  local dir entry
  for dir in "$AGENTS_DIR" "$SKILLS_DIR"; do
    [ -d "$dir" ] || continue
    for entry in "$dir"/*; do
      [ -L "$entry" ] || continue
      points_here "$entry" || continue
      if rm "$entry"; then
        printf 'UNLINK %s\n' "$entry"
        removed=$((removed + 1))
      else
        warn "could not remove $entry"
        failed=$((failed + 1))
      fi
    done
  done
  echo
  echo "Summary: $removed links removed, $failed failed. Nothing else was touched."
}

if [ "$MODE" = "uninstall" ]; then
  uninstall_all
else
  install_all
fi

if [ -n "$WARNINGS" ]; then
  echo
  echo "Warnings:"
  printf '%s' "$WARNINGS"
fi

[ "$failed" -eq 0 ]
