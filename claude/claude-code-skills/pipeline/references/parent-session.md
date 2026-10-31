# The parent session — an iteration run through nested sessions

The default way to work in Claude Desktop. The session the user opens in a pipeline project is the **parent**; each
stage runs in a **nested session** (a «подсессия») with a fresh context. A stage never inherits the context of the
stages before it, the parent's own context stays small, and a long stage hands over to a fresh nested session instead
of being compacted (`references/context.md`).

**The host's rule — who may open a session.** Claude Desktop starts a session at once (`initiation: "user_asked"`)
only in a turn **the user** began — their message, or their click on a proposal card. In a turn another session's
message or an automated note began, it refuses and offers a card instead (`"own_initiative"`): nothing runs until
the user clicks it. This is the app's safety rule, on purpose — a session must never open sessions on another
session's word — and the plugin works inside it, never around it: **every stage's session is opened at the
iteration's start, in the user's own turn, and waits**; a stage then starts by a message («начинай»), which the host
delivers in any turn. No session has to be opened later, so no card stands between two stages, by day or by night.

**Which one am I.** A session whose first message names a parent («родительская сессия — …», «ты — подсессия») is a
nested session: follow «The nested session» below. Any other session is the parent when the host can start sessions
and either the project is a pipeline project — `documentation/.dev-pipeline.json` or `documentation/plans/` (the
session-start hook's test) — or it is a **new project** (no `documentation/` yet) whose request starts the pipeline
(a new product or feature: «давай подумаем», «хочу новую фичу», a brainstorm). The host's tool: Claude Desktop's
`mcp__ccd_session__start_session`, often deferred (load it with ToolSearch `select:mcp__ccd_session__start_session`
before deciding it is absent); the Codex app's equivalent is a separate chat, `mcp__codex_app__create_thread` (the
Codex build's glossary maps the rest). Without such a tool (a terminal) there is no parent: the session runs the
stages itself, as before, and hands over by asking the user (`references/context.md` → step 4).

## The parent

- **It runs no stage.** It reads where the project stands (`scripts/where_am_i.py`, `references/where-am-i.md`),
  starts each stage's session in its turn, and waits. It answers «где я», «что дальше» itself, from the script and the
  sessions' states. A request for work outside the chain — «поправь поле», «нарисуй экран настроек» — gets a session
  of its own, opened in that user turn and titled for that job.
- **Its own id first.** Every prompt names the parent by its session id, the one address a nested session can write
  to (`mcp__ccd_session_mgmt__get_session` with `self` gives it). A name such as «parent» reaches nobody.
- **Its own title: «iteration <version>».** The version comes from the project: an open iteration
  (`scripts/where_am_i.py` — its folder or branch) is continued under its number; a new iteration takes the number
  `references/service-version.md` → Opening the iteration sets — proposed from the documents and the manifest, and
  for a project from zero asked of the user («Номер первой версии?», `0.1.0` recommended), before the list of
  sessions. As soon as the version is known — a new iteration, a continued one, the next one in the same parent —
  the parent renames itself (`mcp__ccd_session_mgmt__set_session_title`, `session_id`
  `self`), so the sidebar shows which session holds the iteration and the stages' titles read under it. When the
  user named the session themselves the app asks them to approve the new title; a declined rename stays declined.
- **The list of sessions — `scripts/subsessions.py`.** Every session has its job and its title before it opens; there
  are no spares. The list lives in `documentation/plans/<version>/sessions.md` (out of git, like the folder) and only
  the script writes it: `plan` (the rows), `set` (an id), `mark` (a state), `parent`, `show`, `whoami`. `plan` adds,
  after each long stage (макеты, ТЗ на экраны, прогон, UI-тесты), its «· часть 2», and after each check that can send
  work back (UI-тесты, аудит) its «исправления … · план», «… · прогон» and «… · повтор» — rows marked «если …»,
  opened with the rest and archived at the close when unused.
- **The iteration's sessions, all at once.** In the turn the user starts or continues the iteration («продолжим»,
  «продолжай», a new parent on a fresh clone):
  1. `python3 scripts/subsessions.py <project> <version> show`. A list with ids from this machine → the iteration
     goes on: the row «идёт» is where the user works, the next «ждёт» is the next stage; rows «не открыта» are
     opened in step 4. No list (a new iteration, a fresh clone, another person's machine — the ids of other
     machines reach nobody) → step 2.
  2. Build the stages **still to run**: from the chain (`SKILL.md` → the chain table, `references/branch-order.md`),
     what the project has (screens or not, a database, an HTTP API, containers, CI already there) and, for an
     iteration already under way, `scripts/where_am_i.py` — its open points name the first stage left; stages before
     it are done. `plan` itself skips a document stage whose documents all carry this version's stamp.
  3. Ask once, as a chat question (`references/question-format.md`): «Подсессии итерации <version>: <the titles
     `plan` would print, in order; the «если …» ones marked>. Открыть все? Ответьте «все» или перечислите, какие
     убрать.» Nothing is opened before the answer. Then `plan` with the kept stages (`--no-parts`, `--no-fixes` when
     the user dropped those).
  4. On the answer — a user turn — open each row «не открыта», in the list's order: locally, in this folder, a fresh
     context, no worktree, `wake_when_done: false`, titled as the row, with the waiting prompt below; record each id
     at once (`set <row> <id>`) and the parent's own (`parent <id>`). Not `true`: it wakes the opener at the end of
     every turn of that session — a closed stage's session spent its turns retelling the next one's work (live run
     2026-10-31). The reports below come by `SendMessage`; a note that a nested session's turn ended, when one comes
     anyway, gets no reply and no retelling.
  5. Send the stage to start «начинай» (`mark <row> идёт`) — on a continued iteration, with «продолжи с <item>» from
     `resume.md` — and tell the user in one line where to work: «Работаем в «<title>» — она в боковом списке».
  If the host refuses or limits the number of sessions, open what it allows in the list's order and the rest later,
  one batch per user turn; say so once.
- **Starting the next stage** — on a report from a nested session (below): `mark` the sender, send the next row
  «начинай» (`SendMessage`, which works in any turn; `mark … идёт`), and the user a line: «Дальше — «<title>» в
  боковом списке». Two branches after the SRS (`references/branch-order.md`): start both, unless the user asked for
  one order.
- **What comes back**, one line each from a nested session (`SendMessage` to the parent):
  - «ЭТАП <stage> ЗАКРЫТ · дальше: <stage>» — `mark … закрыт`, start that stage's row; «· остановиться» — say where
    the iteration stands and start nothing;
  - «<stage> ПЕРЕДАН · после <item> · контекст <N> тыс. · продолжать с <item>» → `mark … передан`, send the stage's
    «· часть 2» row «начинай: продолжи с <item>; состояние — в documentation/plans/<version>/resume.md и git». When part 2
    hands over too: `part <row>` adds «· часть 3»; open it in the next user turn, or offer a card
    (`initiation: "own_initiative"`) and tell the user one click opens it;
  - «ОСТАНОВЛЕНА · <причина>» → tell the user, with the session's title;
  - «ВОПРОС · …» — only when a nested session runs without the user (a chain left for the night,
    `references/unattended.md`): the standing answers settle it, or the user is asked here and the answer sent back.
- **A check that sends work back** (`DEFECTS`, `FIX`): start its «исправления … · план» row, then «… · прогон», then
  «… · повтор» — each on the previous one's report. A check that passes: `mark` its «если …» rows «убран» and archive
  their sessions (`mcp__ccd_session_mgmt__archive_session`). A stage dropped on the way the same.
- **The iteration's close** (`SKILL.md` → End of the pipeline: the last stamp, the site, the summary, the tag,
  `reflect`, the closing lines, the cleanup question) is the last row, «<version> · закрытие». After it, archive the
  rows left unused, report the iteration closed, and open the next iteration when the user asks — the parent's
  context is small enough to carry several. Before the user leaves the work to run alone, collect the standing answers
  (`references/unattended.md`).
- **Before saying anything about a nested session's state**, check it (its status, the progress file, `resume.md`,
  git, `subsessions.py show`) — never from memory.

**Titles** come from `subsessions.py` — the same words every time, so the sidebar reads as the chain: бизнес-требования ·
SRS · схема БД · API · архитектура · каркас · макеты · ТЗ на экраны · тест-кейсы · сверка документов · план · прогон ·
UI-тесты · аудит безопасности · релиз · CI · эксплуатация · закрытие, with «· часть 2», «исправления UI · план», «UI-тесты
· повтор» and the like. The requirements document is «SRS» — never «ТЗ», which the user keeps for the screen specs
(«ТЗ на экраны»).

**The waiting prompt of a session** (Russian, as the user reads it):

```text
Ты — подсессия «<title>» итерации <version> плагина dev-pipeline: <job — «этап <stage>»; «часть 2 этапа <stage>,
начнёт, когда часть 1 передаст работу»; «исправления по отчёту <report>, если он вернёт работу»>. Родительская
сессия — «iteration <version>», id <parent's session id> — пиши ей через SendMessage на этот id. Своё место в списке
находишь сама: python3 <plugin>/pipeline/scripts/subsessions.py <project> <version> whoami <твой id>.
Вопросы пользователю — только сообщением в чате, без карточек выбора.
Сейчас ничего не начинай: ответь одним словом «жду» и закончи ход. Когда придёт «начинай» (от родительской
сессии), запусти /dev-pipeline:<skill> <arguments, or nothing> и работай с пользователем здесь, как обычно. Если в
сообщении «начинай» есть «продолжи с <пункт>» — продолжай с него; состояние — в
documentation/plans/<version>/resume.md и git.
Когда этап закрыт и пользователь ответил на вопрос о следующем этапе, сама его здесь не начинай: напиши
родительской сессии «ЭТАП <stage> ЗАКРЫТ · дальше: <этап>» (или «· остановиться») и закончи. При большом
контексте — передача по pipeline → references/context.md. Остановка — «ОСТАНОВЛЕНА · <причина>».
```

## The nested session

It runs its stage as the stage's skill says, with the user, in this session. What changes:

- **It starts only on «начинай»** — before that its one reply is «жду». Its first message is its card: its title,
  its job, the skill to run, the version, the parent's id. After a compaction, on «продолжай», or when unsure which
  stage it is, it takes its own id (`mcp__ccd_session_mgmt__get_session` with `self`) to `scripts/subsessions.py
  <project> <version> whoami <id>` and goes on with that row's stage from `resume.md` and the progress file.
- **At the stage's close** it asks the transition question as usual (`SKILL.md` → Asking before a transition), then
  sends the parent «ЭТАП <stage> ЗАКРЫТ · дальше: <the answer's stage>» (two, for the branches after the SRS; «·
  остановиться» when the user stops) and ends with one line to the user: «Дальше — «<version> · <stage>» в
  боковом списке». It opens no session, offers no card for one (a card clicked later opened a second session of one
  stage — live run 2026-10-31), and does not run the next stage here.
- **What the next session must know is on disk before the close**: every decision made in this chat is in its
  document (`references/decision-changes.md`) or in the stage's report — the next session starts from the files and
  git, not from this chat.
- **Over the context limit** it hands over: it tells the parent «<stage> ПЕРЕДАН · после <item> · контекст <N> тыс. ·
  продолжать с <item>» and stops (`references/context.md` → When to hand over); the parent starts the stage's «·
  часть 2».
- In the sidebar every session of the iteration shows as one list under the parent, in the order they opened (seen
  in Claude Desktop, 2026-10-31) — opened at the start in chain order, the list reads as the iteration's plan.
