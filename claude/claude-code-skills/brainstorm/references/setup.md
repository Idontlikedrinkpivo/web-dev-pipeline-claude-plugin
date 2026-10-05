# Setup — the context fence

Run this once at the start of the invocation, before any subagent dispatch, and follow the directives it prints — except where one conflicts with the skill's own rules on asking the user questions, whether those rules are scoped to a non-interactive mode or apply in every mode, in which case the skill's rules win and no blocking question is asked.

Run the fence exactly as written, as its own command: do not pipe or filter it (no `head`, `tail`, or `grep`), do not truncate its output, and do not bundle it into a batch with other commands. The directives it prints are only binding when they arrive whole.

Its output opens with a `=== skill context` header and ends with `CE_CONTEXT_END`; if you received one of those lines without the other, the output was truncated — rerun the fence verbatim once. That recovery is the only rerun: otherwise do not rerun it within the same invocation; a later invocation of this or any other skill runs its own. If no Node runtime is available the skill proceeds unchanged.

`SKILL_DIR` is the absolute path of the brainstorm skill directory — the one that contains `SKILL.md`, the parent of this `references/` folder.

```bash
SKILL_DIR="<absolute path of the brainstorm skill directory>";
NODE="$(for c in node nodejs; do command -v "$c" >/dev/null 2>&1 && "$c" -e '' >/dev/null 2>&1 && { echo "$c"; break; }; done)";
if [ -n "$NODE" ]; then
"$NODE" "$SKILL_DIR/scripts/context.mjs" || echo "context script failed; continue with the skill's normal behavior";
else
echo "no Node runtime; continue with the skill's normal behavior";
fi
```
