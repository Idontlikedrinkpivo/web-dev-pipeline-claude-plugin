# The parent session — an iteration run through nested sessions

How the pipeline always runs in Claude Desktop — the user's choice, not a default to opt out of: the session the user
opens in a pipeline project is the **parent**; each stage runs in a **nested session** (a «подсессия») with a fresh context. A stage never inherits the context of the
stages before it, the parent's own context stays small, and a long stage's session is compacted by the host — in `work`
between units (`references/context.md` → Compaction).

**The host's rule — who may open a session.** Claude Desktop starts a session at once (`initiation: "user_asked"`)
only in a turn **the user** began — their message, or their click on a proposal card. In a turn another session's
message or an automated note began, it refuses and offers a card instead (`"own_initiative"`): nothing runs until
the user clicks it. This is the app's safety rule, on purpose — a session must never open sessions on another
session's word — and the plugin works inside it, never around it: **every stage's session is opened at the
iteration's start, in the user's own turn, and waits**; a stage then starts by a message («начинай»), which the host
delivers in any turn. No session has to be opened later, so no card stands between two stages, by day or by night.

## Which one am I

The first step of any session that starts pipeline work, a stage asked for directly included; the first stages'
`SKILL.md` (brainstorm, srs-writer) send here before they read anything. A session whose first message names a
parent («родительская сессия — …», «ты — подсессия», «Ты — чат этапа …») is a nested session: follow «The nested session» below. Any other session is the parent when the host can start sessions
and either the project is a pipeline project — `documentation/.dev-pipeline.json` or `documentation/plans/` (the
session-start hook's test) — or it is a **new project** (no `documentation/` yet) whose request starts the pipeline
(a new product or feature: «давай подумаем», «хочу новую фичу», a brainstorm). The host's tool: Claude Desktop's
`mcp__ccd_session__start_session`, often deferred (load it with ToolSearch `select:mcp__ccd_session__start_session`
before deciding it is absent). Without such a tool (a terminal) there is no parent: the session runs the stages
itself, as before, and the host compacts it in place (`references/context.md` → Compaction).

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
  are no spares. The list lives in `documentation/plans/<version>/sessions.md` (out of git: its session ids are this machine's) and only
  the script writes it: `plan` (the rows), `set` (an id), `mark` (a state), `parent`, `show`, `whoami`, `add` (a «правки» row for a
  closed stage).
  One row per stage, and no parts: a stage over the context limit goes on in its own session, compacted by the host
  (`references/context.md` → Compaction). Pre-opened parts mostly stayed unused (Дашборд руководителя 1.1.0), and a part opened on the way
  needed the user's click each time, which broke an autonomous run (the user, 2026-11-02). No session for fixes
  either: what a check sends back runs inside that check's own session (below).
- **The iteration's sessions, all at once.** In the turn the user starts or continues the iteration («продолжим»,
  «продолжай», a new parent on a fresh clone):
  1. `python3 scripts/subsessions.py <project> <version> show`. A list with ids from this machine → the iteration
     goes on: the row «идёт» is where the user works, the next «ждёт» is the next stage; **every** row «не открыта»
     the script names is opened in step 4, in this same turn, with no new question — the user agreed to the list
     when it was made, and the answer to «что дальше» (`continue` asks it) only picks which session gets
     «начинай». Opening that one alone left the rest for a later turn and a card each (Дашборд руководителя 1.1.0).
     A part the script lists apart («откроются только при передаче работы») stays unopened. No list (a new
     iteration, a fresh clone, another person's machine — the ids of other machines reach nobody) → step 2.
  2. Build the stages **still to run**: from the chain (`SKILL.md` → the chain table, `references/branch-order.md`),
     what the project has (screens or not, a database, an HTTP API, containers, CI already there — but containers
     already there do not drop «релиз»: every version gets its own `release/<version>/`, `deploy-topology` → A
     repeat release; ai-initiatives 2.3.0 went from the audit to the close with no kit) and, for an
     iteration already under way, `scripts/where_am_i.py` — its open points name the first stage left; stages before
     it are done. `plan` itself skips a document stage whose documents all carry this version's stamp.
  3. Ask once, as a chat question (`references/question-format.md`), from the current point — the same wherever the
     work starts: a new project, a stage the user asked for directly («сделай схему БД»), a continued iteration, a
     clone another person picked up. Only the stages left are listed, numbered, so no session opens for work already
     done or not wanted:
     ```
     **Подсессии итерации <version>**
     Сейчас: <the first open point, from where_am_i>. Уже сделано: <the done stages, one line; «ничего» on a start>.
     Осталось:
     1. <title>
     2. <title> — если <condition>
     …
     Какие открыть? Ответьте «все» или номера нужных этапов.
     ```
     A stage the user asked for directly is in the list and marked «— вы просили». When the parent's window is not
     lowered to `context_limit` yet, the same message ends with the window question (`references/context.md` →
     Compaction → The window), and a yes is written before step 4, so the sessions open with it. Nothing is opened
     before the answer. Then `plan` with the chosen stages; a stage left out is not run in this iteration. When a left-out stage
     is a gate a chosen one needs (the chain table), say so in one line and ask once more.
  4. On the answer — a user turn — open each row «не открыта», in the list's order: locally, in this folder, a fresh
     context, no worktree, `wake_when_done: false`, titled as the row, with the waiting prompt below; record each id
     at once (`set <row> <id>`) and the parent's own (`parent <id>`). Not `true`: it wakes the opener at the end of
     every turn of that session — a closed stage's session spent its turns retelling the next one's work (live run
     2026-10-31). The reports below come by `SendMessage`; a note that a nested session's turn ended, when one comes
     anyway, gets no reply and no retelling.
     **The parent's own model and effort** (`mcp__ccd_session_mgmt__get_session` with `self` gives both): pass the
     model to the session tool, and right after opening set the effort the same
     (`mcp__ccd_session_mgmt__set_session_effort` — the parent's own level asks the user nothing) when the new
     session reports another. The user picks them once, on the parent; left to the defaults, the live run's stages
     ran on two models chosen by nobody (2026-10-31). The same for every session opened later — a job outside the chain.
  5. Send the stage to start «начинай» (`mark <row> идёт`) — on a continued iteration, with «продолжи с <item>» from
     `resume.md` — and tell the user in one line where to work: «Работаем в «<title>» — она в боковом списке».
  If the host refuses or limits the number of sessions, open what it allows in the list's order and the rest later,
  one batch per user turn; say so once.
- **Starting the next stage** — on a report from a nested session (below): `mark` the sender, send the next row
  «начинай» (`SendMessage`, which works in any turn; `mark … идёт`), and the user a line: «Дальше — «<title>» в
  боковом списке». Two branches after the SRS (`references/branch-order.md`): start both, unless the user asked for
  one order. A row whose «Когда» says «после API» (the screen specs — `plan` sets it; `subsessions.py … after` for
  any other) is opened with the rest but gets «начинай» only when that stage closes: `mark … закрыт` prints the rows
  it frees. A report that names several stages (the architecture and the screen specs after the API) starts each.

### What comes back

One line each from a nested session (`SendMessage` to the parent):

- «ЭТАП <stage> ЗАКРЫТ · дальше: <stage>[, <stage>]» — `mark … закрыт`, start each named stage's row; «· ждёт:
  <stage> после <stage>» — mark closed, start nothing for that branch: the row waits for the stage it names
  (`references/next-stage.md`); «· остановиться» — say where the iteration stands and start nothing;
- «<stage> ПЕРЕДАН · …» — only from a session on a plugin before 1.2.293: never clear it (in `auto` the classifier
  refused the clear, 2026-11-17); send it «продолжай здесь с <item>: контекст сжимает приложение, не останавливайся»
  and `mark … идёт` (`references/context.md` → Compaction). The parent and its nested sessions stay in one
  permission mode: a session in another mode holds cross-session messages for the user's approval and the chain
  silently stalls, so the parent never changes one session's mode alone;
- «ОСТАНОВЛЕНА · <причина>» → tell the user, with the session's title; then — and on the user's own stop here
  («стоп», «на сегодня всё») — the parent runs `reflect` over the window since its last section, a part «… · часть
  <n>, до <что остановило>» (`reflect` → The section → Its heading; not on a short «подожди»): it alone sees every nested session's end, and a stopped live test otherwise leaves its
  evidence only in transcripts nobody reads later;
- «ВОПРОС · …» — only when a nested session runs without the user (a chain left for the night,
  `references/unattended.md`): the standing answers settle it, or the user is asked here and the answer sent back;
- «РЕШЕНИЕ · <было> → <стало> · решил <кто> · владелец: <stage> · жду» — a decision that changes another
  stage's document (`references/decision-changes.md` → Under a parent session): `mark` the owner stage's row
  «идёт» and send it «РЕШЕНИЕ ИЗМЕНЕНО · <было> → <стало> · решил <кто> · от <stage>»; no live session for that
  stage (closed and archived, a fresh clone) → `subsessions.py … add <stage>` and open «<version> · NN <word>:
  правки» in a user turn, then send it the same — never the owner's writer here, out of the user's sight. On «РЕШЕНИЕ ЗАПИСАНО · <document> ·
  коммит <sha> · задеты: …» → `mark` the owner «закрыт», route each document named the same way, and send the
  waiting session «продолжай: <document> обновлён, коммит <sha>».

### Checks, the close, the state

- **A check that sends work back** (`DEFECTS`, `FIX`) keeps it in its own session: the fix plan (`plan` `MODE fix`,
  its writer agent and `plan-review`), its run (`work`'s executors and reviews) and the check's re-run go on there,
  by agents, and the session reports «ЭТАП … ЗАКРЫТ» only after the re-run passes; over the context limit it hands
  over as any stage. Six sessions for one check's fixes crowded the sidebar for nothing (Дашборд руководителя
  1.1.0). A stage dropped on the way: `mark` it «убран» and archive its session
  (`mcp__ccd_session_mgmt__archive_session`).
- **The iteration's close** (`SKILL.md` → End of the pipeline: the last stamp, the site, the summary, the tag,
  `reflect`, the closing lines, the cleanup question) is the last row, «<version> · закрытие». After it, archive the
  rows left unused, report the iteration closed, and open the next iteration when the user asks — the parent's
  context is small enough to carry several. Before the user leaves the work to run alone, collect the standing answers
  (`references/unattended.md`).
- **Before saying anything about a nested session's state**, check it (its status, the progress file, `resume.md`,
  git, `subsessions.py show`) — never from memory.

**Titles** come from `subsessions.py` — «<version> · <place in the chain, two digits> <word>», «1.0.0 · 02 SRS»,
«1.0.0 · 03 схема БД». The sidebar sorts as the user set it — by name, by creation or by last activity; by name the
words alone put «API» before «SRS» and «архитектура» before «схема БД» (the user, 2026-11-04), so the number keeps the
chain order by name and by creation; by activity the last active comes first, and the plugin does not change the
user's sort. A title keeps the row's words; a topic may follow after a colon («1.0.0 · 02 SRS: письма через
Postbox»), never before the number. The words, in order: бизнес-требования ·
SRS · схема БД · API · архитектура · каркас · макеты · ТЗ на экраны · тест-кейсы · сверка документов · план · разработка
(the plan's run, `work`) · UI-тесты · аудит безопасности · релиз · CI · эксплуатация · закрытие. The requirements document is «SRS» — never «ТЗ», which the user keeps for the screen specs
(«ТЗ на экраны»).

**The waiting prompt of a session** (Russian, as the user reads it):

```text
Ты — подсессия «<title>» итерации <version> плагина dev-pipeline: <job — «этап <stage>»>. Родительская
сессия — «iteration <version>», id <parent's session id> — пиши ей через SendMessage на этот id. Своё место в списке
находишь сама: python3 <plugin>/pipeline/scripts/subsessions.py <project> <version> whoami <твой id> (id — из get_session с «self»; подходит и с «local_», и без).
Вопросы пользователю — только сообщением в чате, без карточек выбора.
Замечания к работе плагина пишите прямо в этот чат, в момент, когда что-то пошло не так: разбор сессий (reflect)
возьмёт их как улики.
Сейчас ничего не начинай: ответь одним словом «жду» и закончи ход. Когда придёт «начинай» (от родительской
сессии), запусти /dev-pipeline:<skill> <arguments, or nothing> и работай с пользователем здесь, как обычно. Если в
сообщении «начинай» есть «продолжи с <пункт>» — продолжай с него; состояние — в
documentation/plans/<version>/resume.md и git.
Перед закрытием этапа убери всё, что он поднял (копии стенда, контейнеры потоков, worktree, временные базы), и
проведи проверку передачи (pipeline → references/handover-check.md).
Когда этап закрыт и пользователь ответил на вопрос о следующем этапе, сама его здесь не начинай: сообщение
родительской сессии печатает python3 <plugin>/pipeline/scripts/subsessions.py <project> <version> closing <ключ
этапа> <следующие этапы | остановиться> — отправь его строку как есть и закончи; отказ скрипта — сначала то, что он
назвал. Решение, которое
меняет документ другого этапа (SRS, схему, API, архитектуру, ТЗ на экран), здесь не правь и его писателя не
запускай: напиши родительской «РЕШЕНИЕ · <было> → <стало> · решил <кто> · владелец: <этап> · жду» и жди
«продолжай»; а на «РЕШЕНИЕ ИЗМЕНЕНО · …» от родительской внеси решение в свой документ своим писателем,
закоммить, отправь и ответь «РЕШЕНИЕ ЗАПИСАНО · <документ> · коммит <sha> · задеты: <документы или «нет»>».
В этой папке работают и другие сессии, индекс git общий: коммить только свои файлы — git add -- <путь> <путь>, затем
git commit -m "…" -- <путь> <путь>, каждый путь отдельным словом.
Файл для другой сессии клади в documentation/plans/<version>/ — не в заметки сессии и не во временную папку: другая
сессия их не видит.
Если вопрос другой сессии ты закрыла сама, без пользователя, скажи ему одной фразой простыми словами, что решено и
почему и что ему делать ничего не нужно — без «вопроса сессии API», id и sha.
Контекст сжимает программа — не останавливайся и не передавай работу (pipeline → references/context.md). Остановка —
«ОСТАНОВЛЕНА · <причина>».
```

## The nested session

It runs its stage as the stage's skill says, with the user, in this session. What changes:

- **It starts only on «начинай»** — before that its one reply is «жду». Its first message is its card: its title,
  its job, the skill to run, the version, the parent's id. After a compaction, on «продолжай», or when unsure which
  stage it is, it takes its own id (`mcp__ccd_session_mgmt__get_session` with `self`) to `scripts/subsessions.py
  <project> <version> whoami <id>` and goes on with that row's stage from `resume.md` and the progress file.
- **At the stage's close** it asks the transition question as usual (`SKILL.md` → Asking before a transition), runs
  the handover check — a read-only agent compares this chat with the files and names a decision no file holds
  (`references/handover-check.md`); each one is written down and committed — removes what the stage started
  (`references/handover-check.md` → The stage's leftovers) — then sends the parent the line `scripts/subsessions.py
  … closing` printed (it refuses without the check or with leftovers): «ЭТАП <stage> ЗАКРЫТ · дальше: <the answer's stages — those ready now, `references/next-stage.md`>» (two, for the branches after the SRS; «· ждёт: <stage> после <stage>» when none can start; «·
  остановиться» when the user stops) and ends with one line to the user: «Дальше — «<version> · <stage>» в
  боковом списке». It opens no session, offers no card for one (a card clicked later opened a second session of one
  stage — live run 2026-10-31), and does not run the next stage here.
- **What the next session must know is on disk before the close**: every decision made in this chat is in its
  document (`references/decision-changes.md`) or in the stage's report — the next session starts from the files and
  git, not from this chat.
- **A decision that belongs to another stage's document** (`references/decision-changes.md` → The owner) is not
  edited here and its writer is not dispatched here: it goes to the parent as «РЕШЕНИЕ · … · владелец: <stage> ·
  жду», and this session waits for «продолжай» (`references/decision-changes.md` → Under a parent session). A
  closed session that gets «РЕШЕНИЕ ИЗМЕНЕНО · …» from the parent edits its document through its writer, commits,
  pushes and reports «РЕШЕНИЕ ЗАПИСАНО · <document> · коммит <sha> · задеты: …».
- **One tree, one index.** Its commits name their own paths (`SKILL.md` → Commit each document): `git add -- <paths>`,
  then `git commit -m "…" -- <paths>`, each path a separate word — a plain `git commit` took another session's
  staged files twice in 2.3.0.
- **A file for another session** goes to `documentation/plans/<version>/` — never to the session's notes or a
  scratch folder, which the other session cannot read (2.3.0: a gaps list for the parent had to be copied over).
- **A question settled without the user** — another session's, answered from the documents — is told to the user in
  one plain sentence: what was decided, why, and that nothing is needed from them. Not «ответил на вопрос сессии
  API» with ids and shas: the user did not know what that meant (2.3.0).
- **The context never stops it.** It does not measure the context to hand over, pause or ask: the host compacts it
  — in `work` after the unit in flight is committed — and it picks up from `resume.md`, the progress file and git
  (`references/context.md` → Compaction). It writes what the chat settles to its file at once, so any moment is safe
  to compact. It runs in the parent's permission mode: a session in another mode holds cross-session messages for
  the user's approval, which silently stalls the chain.
- In the sidebar every session of the iteration shows as one list under the parent (seen in Claude Desktop,
  2026-10-31), in the user's sort: by name or by creation the titles' numbers make it read as the iteration's plan.
