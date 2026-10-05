# Visual Probes

Use visual probes when a brainstorm decision is faster to judge by seeing a rough artifact than by reading prose. A visual probe is a disposable decision sketch, not a prototype, implementation plan, UI spec, or design deliverable.

## Trigger

Use this reference only when the next question has a specific visual decision:

- behavior shape: "Which annotation or drawing behavior feels right?"
- layout shape: "Which navigation structure matches the workflow?"
- flow shape: "Where should this decision point sit?"
- state shape: "Which empty/loading/error state communicates the right thing?"
- diagram shape: "Which relationship or system boundary is clearer?"

Do not use a visual probe for product goals, scope boundaries, success criteria, evidence probes, tradeoff prose, or technical decisions that are easier to discuss in chat.

## The gate (when the offer must fire)

When the Phase 0.3 tripwire flagged an inherently-visual topic, the offer must fire before the **first** decision about shape, behavior, state, layout, flow, or a diagram is raised in *any* form — plain chat or a blocking question.

**Timing is state-based, not memory-based.** Anchor the check to the decision you are about to raise, not to a "pending gate" remembered since Phase 0.3: offer unless this specific decision has already been through the offer (the user already chose text or visual for it). This gate takes precedence over the next question — do not raise the shape decision until the user has declined visual (or visual feedback has returned to chat).

**An ASCII preview or text mockup embedded inside the question's choices does NOT satisfy the offer** — that shortcut is exactly what this gate exists to stop. The offer is its own prior question with two options (sketch vs describe); only after the user chooses does the shape decision proceed.

## Offer

Ask once at the decision point. Do not enable a session-wide mode.
Follow `grill-me` → "How a question is shown": one question in the chat,
in Russian. The user answers by sending a message. Do not open a card.

In the chat, explain both options. A visual sketch is a rough picture in
the browser so the shape can be judged by looking. A text description
keeps the same decision in words, which is faster and less precise.

- **A. Набросать эскиз.** Грубые варианты в локальном браузере.
- **B. Описать словами.** Решение остаётся в чате.

Recommend one in a sentence. The text path must be credible. If you cannot
explain the decision clearly in text, you do not understand it well enough
to sketch it.

The chat block is the whole question. Do not open a question card.

If the user chooses text, continue in chat and do not re-offer for the same decision. If they choose visual, proceed below.

## Visual Path

Create the cheapest artifact that answers the current question. Optimize for fast feedback, not polish.

Allowed:

- rough behavior sketches
- low-fidelity wireframes
- state comparisons
- flow diagrams
- simple A/B/C visual contrasts
- disposable interaction demos only when behavior itself is the decision

Avoid:

- polished branding
- final colors or typography
- component-library precision
- pixel-perfect layout
- production-like implementation
- unnecessary animation
- details that imply exact UI commitments

Label the artifact as directional. State what the user should judge and what they should ignore.

## Display Helper

Use the bundled display-only helper when the current platform can run a bundled skill script. Invoke it via the `SKILL_DIR` anchor: set `SKILL_DIR` to the absolute path of the directory containing the `brainstorm` `SKILL.md` you loaded (the Bash tool's cwd is the user's project, not the skill dir), and re-set it in the same command on each call since shell vars don't persist between Bash invocations. Do not resolve the helper from the user's project CWD.

Start (detached):

```bash
SKILL_DIR="<absolute path of the brainstorm skill directory>";
SCRATCH_ROOT="/tmp/brainstorm-$(id -u)";
if [ -L "$SCRATCH_ROOT" ]; then echo "unsafe scratch root symlink: $SCRATCH_ROOT" >&2; exit 1; fi;
(umask 077; mkdir -p "$SCRATCH_ROOT") || exit 1;
if [ -L "$SCRATCH_ROOT" ] || [ ! -O "$SCRATCH_ROOT" ]; then echo "scratch root is not owned by the current user: $SCRATCH_ROOT" >&2; exit 1; fi;
chmod 700 "$SCRATCH_ROOT" || exit 1;
PROBE_DIR="$SCRATCH_ROOT/brainstorm-visual/<run-id>"; (umask 077; mkdir -p "$PROBE_DIR") || exit 1; chmod 700 "$PROBE_DIR" || exit 1;
node "$SKILL_DIR/scripts/visual-probe-server.mjs" start --root "$PROBE_DIR"
```

Append `--foreground` to that `start` command for foreground mode. Status and stop take the same anchor — and because `SKILL_DIR` does not persist between Bash invocations, each must re-set it in its own call rather than reuse the `start` block's value:

```bash
SKILL_DIR="<absolute path of the brainstorm skill directory>";
SCRATCH_ROOT="/tmp/brainstorm-$(id -u)";
if [ -L "$SCRATCH_ROOT" ]; then echo "unsafe scratch root symlink: $SCRATCH_ROOT" >&2; exit 1; fi;
(umask 077; mkdir -p "$SCRATCH_ROOT") || exit 1;
if [ -L "$SCRATCH_ROOT" ] || [ ! -O "$SCRATCH_ROOT" ]; then echo "scratch root is not owned by the current user: $SCRATCH_ROOT" >&2; exit 1; fi;
chmod 700 "$SCRATCH_ROOT" || exit 1;
PROBE_DIR="$SCRATCH_ROOT/brainstorm-visual/<run-id>"; (umask 077; mkdir -p "$PROBE_DIR") || exit 1; chmod 700 "$PROBE_DIR" || exit 1;
node "$SKILL_DIR/scripts/visual-probe-server.mjs" status --root "$PROBE_DIR"
# stop: the same command with `stop` in place of `status` (re-set SKILL_DIR again)
```

If `SKILL_DIR` cannot be resolved to a concrete skill directory, do not guess from the project CWD — use the text path.

The helper creates `screens/` and `state/`, serves the newest `.html` file in `screens/`, writes `state/display-info.json`, and exposes `/version` so the browser can poll for screen changes. The browser reloads only when the newest screen changes; it must not continually reload on a timer. `/version` polling does not count as activity, so an abandoned browser tab cannot keep the server alive forever. Detached servers monitor the owning harness process when it can be resolved, and all servers exit after an idle timeout. The helper has no click tracking or browser-to-agent event path.

If the helper path is unavailable or the platform cannot display a local URL cleanly, say so briefly and use the text path. Do not build a custom event system or long-lived server to compensate during the brainstorm.

## Launch Mode by Platform

The server is the same everywhere; only the launch mode changes.

- **Claude Code / Claude desktop app:** detached `start` is the default path. If the app opens localhost URLs, show the returned URL and continue. If the browser surface is unavailable, use the text path.
- **Plain terminal UI:** print the returned URL for the user to open manually. If opening a browser would interrupt the flow, keep the decision in chat.
- **Remote or containerized sessions:** if `localhost` is not reachable from the user's browser, start with `--host 0.0.0.0` and tell the user which host/port to open. If that cannot be made clear, use the text path.

Never force the visual path because a local server exists. The user chose visual to understand the decision faster; if the platform plumbing gets in the way, switch back to text.

## Post-Artifact Feedback

After showing the visual artifact, ask for bounded artifact feedback as one chat question per Rule 4. This is still chat-based feedback, not browser event capture.

Offer options when the expected response is a small choice set:

- A/B/C/D option selection
- visual direction vs mix
- choose one layout/state/behavior
- accept one option with requested tweaks

Their message is the answer, including their own text. When feedback is genuinely open critique, ask it with no options.

Good post-artifact question, in the chat, in Russian. Name what A, B, C, and D each show, in words a reviewer can judge without opening the code. Keep the terms for the sketches. Explain what "mix" means: take parts of more than one sketch. One question, then stop. The user answers by sending a message. Do not open a question card. Judge the behavior shape, not the exact styling.

Do not ask the user to click inside the browser artifact. The explanation of each sketch stays in the chat.

## Interaction Contract

The browser/artifact is display-only. Feedback happens in chat.

Do not add click tracking, selected states, event ingestion, forms, analytics, or "submit" affordances in v1. Do not ask the user to click an option inside the browser artifact. The choice is their next message; what each option means is written in the chat.

A minimal version, after showing the artifact:

> I’m showing three rough options. Reply here with A, B, C, or "mix", plus anything that feels off. Judge the behavior shape, not the exact styling.

The user's chat response is authoritative. The visual artifact is supporting context only.

## File Placement

Use OS temp by default because visual probes are disposable scratch:

```text
<scratch-root>/brainstorm-visual/<run-id>/
  screens/
    001-<decision>.html
  state/
    display-info.json
```

Use `.context/brainstorm-visual/<run-id>/` only when the user explicitly wants to inspect, preserve, or curate the sketches after the session. The probe is disposable scratch; the durable artifact is the Phase 3 business requirements document under `documentation/requirements/`.
