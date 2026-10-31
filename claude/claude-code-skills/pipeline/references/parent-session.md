# The parent session — an iteration run through nested sessions

The default way to work in Claude Desktop. The session the user opens in a pipeline project is the **parent**; each
stage runs in a **nested session** (a «подсессия») with a fresh context, opened by the parent and shown under it in
the sidebar. A stage never inherits the context of the stages before it, the parent's own context stays small, and
a long stage hands over to a fresh nested session instead of being compacted (`references/context.md`).

**The host's rule — who may open a session.** Claude Desktop starts a session at once (`initiation: "user_asked"`)
only in a turn **the user** began — their message, or their click on a proposal card. In a turn another session's
message or an automated note began, it refuses and offers a card instead (`"own_initiative"`): nothing runs until
the user clicks it. This is the app's safety rule, on purpose — a session must never open sessions on another
session's word — and the plugin works inside it, never around it: the session in which the user answered opens the
next one, and for the turns without the user the parent keeps a reserve of waiting sessions, opened in the user's
own turns and woken by message later.

**Which one am I.** A session whose first message names a parent («родительская сессия — …», «ты — подсессия») is a
nested session: follow «The nested session» below. Any other session in a project with `documentation/.dev-pipeline.json` or
`documentation/plans/` (the session-start hook's test) is the parent — when the host can start sessions: Claude Desktop's
`mcp__ccd_session__start_session`, often deferred (load it with ToolSearch `select:mcp__ccd_session__start_session`
before deciding it is absent); the Codex app's equivalent is a separate chat, `mcp__codex_app__create_thread`
(the Codex build's glossary maps the rest). Without such a tool (a terminal) there is no parent: the session runs
the stages itself, as before, and hands over by asking the user (`references/context.md` → step 4).

## The parent

- **It runs no stage.** It reads where the project stands (`scripts/where_am_i.py`, `references/where-am-i.md`),
  decides the next stage by the chain, opens a nested session for it, and waits. It answers «где я», «что дальше»
  itself, from the script and the nested sessions' states. A request for work — «поправь поле», «нарисуй экран
  настроек» — becomes a nested session too.
- **Its own id first.** Every prompt names the parent by its session id, the one address a nested session can
  write to (`mcp__ccd_session_mgmt__get_session` with `self` gives it; a nested session that opens the next stage
  passes the same id on). A name such as «parent» reaches nobody.
- **Opening a nested session** — in a turn the user began (their request in this session, their click): locally,
  in this folder, a fresh context, no worktree, `wake_when_done: true` (a note comes back when its turn ends); the title «<version> ·
  <stage>» («2.3.0 · ТЗ», «2.3.0 · макеты», «2.3.0 · прогон, часть 2»); the prompt below. One line to the user:
  which stage opened and that they work in it — the link to the new session from the tool's result.
- **Two branches after the SRS** (`references/branch-order.md`): the design branch and the backend branch are two
  nested sessions at once, when the user did not ask for one order.
- **What comes back**, one line each from a nested session (`SendMessage` to the parent):
  - «ЭТАП <stage> ЗАКРЫТ · следующий открыт: <title>» — the nested session opened the next stage itself, on the
    user's answer (below): note it and wait; «… · остановиться» — say where the iteration stands;
  - «ЭТАП <stage> ЗАКРЫТ · следующий: <stage>, не открыт» — no user turn could open it: wake a reserve session
    for it (The reserve, below); with the reserve empty, offer it as a card (`initiation: "own_initiative"`) and
    tell the user one click opens it;
  - «<stage> ПЕРЕДАН · после <item> · контекст <N> тыс. · продолжать с <item>» → wake a reserve session with
    «продолжи <stage>», else a card «<version> · <stage>, часть <n+1>»;
  - «ОСТАНОВЛЕНА · <причина>» → tell the user, with the session's link;
  - «ВОПРОС · …» — only when a nested session runs without the user (a chain left for the night,
    `references/unattended.md`): the standing answers settle it, or the user is asked here and the answer sent back.
- **The iteration's close** (`SKILL.md` → End of the pipeline: the last stamp, the site, the summary, the tag,
  `reflect`, the closing lines, the cleanup question) runs in its own nested session «<version> · закрытие». The
  parent then reports the iteration closed, and may open the next iteration's first stage when the user asks — its
  context is small enough to carry several iterations.
- **The reserve — waiting sessions opened ahead.** In every turn the user begins in this session (the iteration's
  start, a question, any message), after answering, top the reserve up: waiting nested sessions not tied to a stage,
  titled «<version> · резерв <n>», each with the prompt «Ты — резервная подсессия итерации <version> плагина
  dev-pipeline; родительская сессия — «<title>», id <its session id> (SendMessage на этот id). Жди: не начинай ничего, пока родитель не напишет «начинай» с
  заданием. Сейчас ответь одним словом «жду» и закончи ход.» Keep as many as the rest of the iteration may need with
  nobody there to click: the stages left in the chain plus one per ~4 plan units left (hand-overs), at most 12 — an
  idle one costs only its start. A message wakes a session even in an automated turn, so when a stage has to start
  and no user turn opened it (a «… не открыт» report, a hand-over), take the oldest reserve session: rename it
  «<version> · <stage>» (`mcp__ccd_session_mgmt__set_session_title`, when the host has it) and send it «начинай: <the
  nested-session prompt below>». Only an empty reserve falls back to a card. At the iteration's close, archive the
  reserve left unused (`mcp__ccd_session_mgmt__archive_session`). Before the user leaves the work to run alone,
  collect the standing answers (`references/unattended.md`).
- **Before saying anything about a nested session's state**, check it (its status, the progress file,
  `resume.md`, git) — never from memory.

**The prompt of a nested session** (Russian, as the user reads it):

```text
Ты — подсессия итерации <version> плагина dev-pipeline. Родительская сессия — «<parent's title>», id <parent's
session id> — пиши ей через SendMessage на этот id.
Этап: <stage> — запусти /dev-pipeline:<skill> <arguments, or «продолжи», or nothing>.
<For a continuation: продолжай с <item>; состояние — в documentation/plans/<version>/resume.md и git.>
Работай с пользователем здесь, как обычно. Когда этап закрыт и пользователь ответил на вопрос о следующем этапе,
сама этот этап здесь не начинай: открой для него новую подсессию (pipeline → references/parent-session.md, с тем же
родителем), напиши родительской сессии «ЭТАП <stage> ЗАКРЫТ · следующий открыт: <название>» и закончи. При
большом контексте — передача по pipeline → references/context.md. Остановка — «ОСТАНОВЛЕНА · <причина>».
```

## The nested session

It runs its stage as the stage's skill says, with the user, in this session. What changes:

- **At the stage's close** it asks the transition question as usual (`SKILL.md` → Asking before a transition). The
  user's answer is a turn the user began, so this session **opens the next stage's nested session itself**, with the
  prompt below and the same parent named (two, for the branches after the SRS), and does not run that stage here.
  Then it sends the parent «ЭТАП <stage> ЗАКРЫТ · следующий открыт: <title>» and ends with one line to the user:
  continue in that session (its link). When it was woken by the parent rather than the user (a night run), it does
  not open anything: «ЭТАП <stage> ЗАКРЫТ · следующий: <stage>, не открыт» — the parent wakes a reserve session.
- **What the next session must know is on disk before the close**: every decision made in this chat is in its
  document (`references/decision-changes.md`) or in the stage's report — the next nested session starts from the
  files and git, not from this chat.
- **Over the context limit** it hands over: in a turn the user began, it opens its continuation itself
  («<version> · <stage>, часть <n+1>», «продолжи <stage>») and tells the parent «ПЕРЕДАН · открыта: <title>»;
  otherwise it tells the parent «<stage> ПЕРЕДАН · …» and stops (`references/context.md` → When to hand over).
- The sessions it opens sit under it in the sidebar — the tree reads as a ladder of stages; every one names the
  same parent, which keeps the overview.
