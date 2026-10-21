#!/bin/sh
# dev-pipeline: re-anchor a session on the pipeline's rules after a start, a resume, /clear or a context
# compaction. Prints a few lines into the session's context when the project has an open iteration
# (documentation/plans/<version>/ without summary.md); prints nothing otherwise. Read-only.
set -u
dir="${CLAUDE_PROJECT_DIR:-$PWD}"
plans="$dir/documentation/plans"
[ -d "$plans" ] || exit 0

src=$(cat 2>/dev/null | sed -n 's/.*"source"[[:space:]]*:[[:space:]]*"\([a-z]*\)".*/\1/p' | head -n 1)

open=""
for v in "$plans"/*/; do
  v=${v%/}; name=${v##*/}
  case "$name" in archive|*[!0-9.]*) continue ;; esac
  [ -f "$v/summary.md" ] || open="$open $name"
done
open=${open# }
[ -n "$open" ] || exit 0

stage_of() {
  case "$1" in
    progress.md) echo "work" ;;
    progress-e2e.md) echo "work (browser suite)" ;;
    progress-design.md) echo "ui-design" ;;
    progress-screen-specs.md) echo "screen-spec" ;;
    progress-test-cases.md) echo "ui-test-cases (write)" ;;
    test-run.md) echo "ui-test-cases (run)" ;;
    progress-architecture.md) echo "clean-architecture-design" ;;
    progress-scaffold.md) echo "repo-scaffold" ;;
    progress-deploy.md) echo "deploy-topology" ;;
    security-audit.md) echo "security-audit" ;;
    docs-consistency.md) echo "docs-consistency" ;;
    plan.md|plan-review.md) echo "plan" ;;
    *) echo "" ;;
  esac
}

v=$(printf '%s\n' $open | sort -t. -k1,1n -k2,2n -k3,3n | tail -n 1)
n=$(printf '%s\n' $open | grep -c .)
last=$(cd "$plans/$v" 2>/dev/null && ls -t progress*.md test-run.md security-audit.md docs-consistency.md plan-review.md plan.md 2>/dev/null | head -n 1)
stage=""
[ -n "$last" ] && stage=$(stage_of "$last")

case "$src" in
  compact) why="The context was just compacted: the rules of the skills read earlier are not in the summary." ;;
  clear) why="The context was just cleared." ;;
  resume) why="This session was resumed." ;;
  *) why="A new session in a project with an open iteration." ;;
esac

if [ "$n" -gt 1 ]; then
  echo "dev-pipeline: $n open iterations ($open); the newest is $v (documentation/plans/$v/). The older ones have no summary.md — the pipeline asks which is current before stamping anything."
else
  echo "dev-pipeline: open iteration $v (documentation/plans/$v/)."
fi
if [ -n "$stage" ]; then
  echo "Last stage by its files: $stage — progress in documentation/plans/$v/$last."
fi
echo "$why Before continuing pipeline work, read the dev-pipeline:pipeline skill and the current stage's skill again; take the state from the files on disk, not from memory."
echo "Most often lost: give a stage's progress only as a clickable link to its page — the progress file's name in .html beside the .md (progress-design.html), never the .md; commit a finished document before asking about the next stage or stopping; end a turn only with the next step already running, unless the turn ends on a question to the user; stop every Monitor or background wait you started when its work ends."
[ -f "$plans/$v/resume.md" ] && echo "A run left documentation/plans/$v/resume.md: read it first and check each claim against git, the tree and docker before continuing (pipeline → references/pause-and-resume.md)."
[ -f "$dir/.claude/skills/verify/SKILL.md" ] && echo "This project has .claude/skills/verify: run its doctor before driving the app."
exit 0
