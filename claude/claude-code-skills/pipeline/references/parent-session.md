# The parent session — an iteration run through nested sessions

The default way to work in Claude Desktop. The session the user opens in a pipeline project is the **parent**; each
stage runs in a **nested session** (a «подсессия») with a fresh context, opened by the parent and shown under it in
the sidebar. A stage never inherits the context of the stages before it, the parent's own context stays small, and
a long stage hands over to a fresh nested session instead of being compacted (`references/context.md`).

**Which one am I.** A session whose first message names a parent («родительская сессия — …», «ты — подсессия») is a
nested session: follow «The nested session» below. Any other session in a project with `documentation/` or
`documentation/.dev-pipeline.json` is the parent — when the host can start sessions: Claude Desktop's
`mcp__ccd_session__start_session`, often deferred (load it with ToolSearch `select:mcp__ccd_session__start_session`
before deciding it is absent). Without that tool (a terminal, Codex for now) there is no parent: the session runs
the stages itself, as before, and hands over by asking the user (`references/context.md` → step 4).

## The parent

- **It runs no stage.** It reads where the project stands (`scripts/where_am_i.py`, `references/where-am-i.md`),
  decides the next stage by the chain, opens a nested session for it, and waits. It answers «где я», «что дальше»
  itself, from the script and the nested sessions' states. A request for work — «поправь поле», «нарисуй экран
  настроек» — becomes a nested session too.
- **Opening a nested session.** Locally, in this folder, a fresh context, no worktree; the title «<version> ·
  <stage>» («2.3.0 · ТЗ», «2.3.0 · макеты», «2.3.0 · прогон, часть 2»); the prompt below. One line to the user:
  which stage opened and that they work in it — the link to the new session from the tool's result.
- **Two branches after the SRS** (`references/branch-order.md`): the design branch and the backend branch are two
  nested sessions at once, when the user did not ask for one order.
- **What comes back**, one line each from a nested session (`SendMessage` to the parent):
  - «ЭТАП <stage> ЗАКРЫТ · следующий: <the stage the user chose at the transition question> | остановиться» →
    open the next one, or stop and say where the iteration stands;
  - «<stage> ПЕРЕДАН · после <item> · контекст <N> тыс. · продолжать с <item>» → open «<version> · <stage>, часть
    <n+1>» with «продолжи <stage>»;
  - «ОСТАНОВЛЕНА · <причина>» → tell the user, with the session's link;
  - «ВОПРОС · …» — only when a nested session runs without the user (a chain left for the night,
    `references/unattended.md`): the standing answers settle it, or the user is asked here and the answer sent back.
- **The iteration's close** (`SKILL.md` → End of the pipeline: the last stamp, the site, the summary, the tag,
  `reflect`, the closing lines, the cleanup question) runs in its own nested session «<version> · закрытие». The
  parent then reports the iteration closed, and may open the next iteration's first stage when the user asks — its
  context is small enough to carry several iterations.
- **Before saying anything about a nested session's state**, check it (its status, the progress file,
  `resume.md`, git) — never from memory.

**The prompt of a nested session** (Russian, as the user reads it):

```text
Ты — подсессия итерации <version> плагина dev-pipeline. Родительская сессия — «<parent's title>».
Этап: <stage> — запусти /dev-pipeline:<skill> <arguments, or «продолжи», or nothing>.
<For a continuation: продолжай с <item>; состояние — в documentation/plans/<version>/resume.md и git.>
Работай с пользователем здесь, как обычно. Когда этап закрыт и пользователь ответил на вопрос о следующем этапе,
следующий этап сама не начинай: напиши родительской сессии одну строку
«ЭТАП <stage> ЗАКРЫТ · следующий: <выбор пользователя>» и закончи. При большом контексте — передача по
pipeline → references/context.md: «<stage> ПЕРЕДАН · …» родителю. Остановка — «ОСТАНОВЛЕНА · <причина>».
```

## The nested session

It runs its stage as the stage's skill says, with the user, in this session. What changes:

- **At the stage's close** it asks the transition question as usual (`SKILL.md` → Asking before a transition), and
  after the answer does **not** start the next stage: it sends the parent «ЭТАП <stage> ЗАКРЫТ · следующий:
  <the answer>» and ends its turn with one line to the user that the parent opens the next stage.
- **What the next session must know is on disk before the close**: every decision made in this chat is in its
  document (`references/decision-changes.md`) or in the stage's report — the next nested session starts from the
  files and git, not from this chat.
- **Over the context limit** it hands over through the parent (`references/context.md` → When to hand over,
  step 2).
- It never opens nested sessions of its own: the parent opens every one, so the tree stays one level deep.
