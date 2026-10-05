# Workflow spine — the user-visible task list

Read at Phase 0.4, once a task-tracking tool was found (`TaskCreate` / `TaskUpdate` / `TaskList`). Which tiers get a spine, and what to do without a tool, are in SKILL.md → 0.4.

## The five tasks, in order

1. Check what already exists
2. Ask scoping questions
3. Weigh approaches and recommend
4. Confirm scope before writing
5. Write the requirements plan

## Conditional tasks

**Conditional work earns a task only when its gate fires** — never at creation, and never as a placeholder for a branch that may not run. A branch earns one when the user is either waiting on it or would be surprised to learn it happened: an accepted blindspot pass, a Phase 2.6 verifier working in the background. A step that fires per-decision rather than once does not — it would thrash the list. Insert it at the position where it runs.

**Name every task you add the way the spine is named:** verb first, five words or fewer, naming the outcome the user can hold you to — not the phase, the internal activity, or the tool. `Verify claims against the code`, not `Phase 2.6 claim verification`. Never restate counts, quotas, or pacing in a name; that contract lives in the phase that owns it.

## Skipped tasks

**When a gate resolves such that a listed task will not run, record the skip — never mark it plainly complete, and never let it vanish unexplained.** In order of preference: set a `cancelled` or `skipped` status if the harness has one; otherwise rename the task to name the skip (`Skipped: no doc warranted`) and then mark it complete; only if the name cannot be changed, delete it. Say why in the conversation either way — the list carries the fact, not the reason. If Phase 3 decides no doc is warranted, that is task 5. A task you find yourself skipping routinely is misnamed: it encodes a branch rather than an outcome, so rename it to what happens in the common case.

The list is a view for the user, not an instruction to you. It does not change when a phase fires or what that phase requires, and it never substitutes for a phase's own exit condition.
