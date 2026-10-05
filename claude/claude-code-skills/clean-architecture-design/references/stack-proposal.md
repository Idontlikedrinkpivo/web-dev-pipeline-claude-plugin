# Stack proposal (Step 2b)

Read this when the stack is not already a fact and Step 2b has to propose
cards in chat. The orchestrator runs it in the session chat before any
writer is dispatched; a writer never guesses a framework.

## Why the stack is asked, not picked

The file tree, composition-root wiring, and boundary linter are
stack-shaped. Do not invent a default framework.

If the stack is not already a fact, stop after Step 2 and propose in
chat. Domain model onward waits for that pick. If it is already a fact,
write it into §1 Стек and continue. Do not emit a stack-decision heading.

## Gather constraints first

Do not propose in a vacuum:

1. **Brownfield** — a `package.json`, `pyproject.toml`, `go.mod`,
   `*.csproj`, `Gemfile`, or `pom.xml` in the repo is a fact, not a
   suggestion. Read it.
2. **Already stated** — the user named a stack in this session, or the
   SRS / business-requirements document already committed to one. Write
   that stack in §1 Стек and continue. Do not stop for a chat pick
   when the stack is already a fact. Propose an alternative only if the
   named stack cannot meet a stated NFR.
3. **SRS constraints only** — team language, hosting, latency, compliance,
   "this repo". Not a framework name unless the SRS actually named one.
4. **Nothing found** — still propose; still do not pick silently.

## Brownfield

The first card is "stay on what the repo already uses", with a comment
on what that costs. A migration card exists only if the user asked to
leave, or the current stack cannot meet a stated NFR. Do not present a
free-choice catalog on a live codebase.

## What may go on a card

Every technology on a greenfield card — runtime, framework, database,
frontend framework, and any library a card names — is **widely used and has
complete official documentation** (guides plus an API reference for the
current major, kept up to date). Why: agents write this code from current
docs, not memory, and later stages check version-sensitive behaviour live
(the context7 MCP); a niche or thinly documented library means guessed APIs
and stale answers. Popular means broad adoption and active releases, not a
trend: when in doubt, check weekly downloads or the registry's equivalent and
the date of the last release. A candidate that fails this is dropped in one
line ("not offered — small user base / no API reference for the current major").

This filters proposals only. A stack that is already a fact (brownfield
manifest, named by the user or the SRS) is written as is; if it fails the
criterion, say so once in the comment and continue.

## Greenfield

Offer **two or three viable cards**, not a radar. Drop a candidate in
one line ("not offered — no one on the team writes this" / "breaks
NFR-…") instead of a full card. Each card states, in this order:

| Field | What to name |
|---|---|
| Language + runtime | the language, its runtime and major version (`Node 22`, `Python 3.13`, `Go 1.24`), not "backend" |
| HTTP framework | one concrete framework, with its major version |
| Database | one engine (Postgres unless a constraint forbids it), with its major version |
| Local run | Compose or not — and what processes it starts |
| Boundary linter | the tool this skill maps to that stack, with the major its sketch in `machine-checkable-boundaries.md` targets |
| Frontend | only when the system has a human-facing UI: React + Vite (an app behind a login with a separate backend) or Next.js (public pages that need SEO or server rendering), with its major — the two stacks the `frontend` skill has profiles for and the Figma frames' shadcn/ui style matches. Offer another framework only when the repo already uses one (brownfield) |

Majors matter because the lint sketches are written against them
(go-arch-lint schema v3, golangci-lint config `version: "2"`,
dependency-cruiser options), and `repo-scaffold` installs exactly the
majors §1 Стек names.

Then a **comment**: which constraints it satisfies, what it costs versus
the other cards, the main risk. No essay.

## Asking

When no stack is already a fact: mark **one card as recommended** and
say why in one or two sentences. Follow `grill-me` → "How a question is
shown". The full cards stay in the chat, each term (language, framework,
database, Compose, linter) explained by what it changes for this system.
Each option is a short name of one card, with ` (Recommended)` on the
one you marked. One question, then stop. The user answers by sending a
message. Do not open a question card. Do not dispatch the foundation writer on a
guess. When the
stack is already stated (case 2 above), skip the wait.

ORM, broker, queue — mention on a card only when a port in this design
cannot be drawn without them. They are not a fourth required field.

## After the user picks

Write the chosen stack into §1 Стек (technology + major version + why
it fits this app). Record the pick as the «Стек» row of §1 «Ключевые
решения»; its «Вместо» cell names the cards the user did not pick, one
sentence, not the chat comparison. Adapter client libraries that are
not the runtime stack go under foundation §4 Сборка. Local run goes under
§5, the boundary linter under §6. Do not paste the chat comparison into the
file. Then dispatch the foundation writer. The file tree (§5) and the
lint table (§6) must match this choice.
