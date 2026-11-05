---
name: react
description: >-
  Internal: React rules (derived state, effects only for outside systems, data hooks); read by work's executors before
  React code.
---

# React

`frontend` says what a screen must do; this skill says how its React code stays changeable. The rules come from
react.dev (Rules of React, You Might Not Need an Effect, Choosing the State Structure) and from what an audit of a
real project found: one oversized page holding all its state and effects, network calls in components, a reference
list loaded several ways. Examples «так / не так»: `references/examples.md`.

## Essentials

Read first, in full; the sections below hold the detail — the packet names the ones this unit needs.

- Server data only through the data layer: one query hook per read `operationId`, a mutation per write; a component
  never fetches → The reviewer checks 3.
- After a successful mutation, invalidate (or `setQueryData`) the list and the item it changed — the user must never
  need a reload → The reviewer checks 4.
- Do not store what you can compute, and do not copy server data into `useState` → The reviewer checks 1, 5.
- An effect only synchronizes with an outside system; what the user did is handled in the event handler
  → The reviewer checks 2.
- A page is a data hook `use<Screen>()` plus a view that knows nothing of the API → The reviewer checks 7.
- A form is React Hook Form with one schema from the generated request type; a format rule is imported, never a regex
  typed in → The reviewer checks 12.
- What the user may do comes from the response when the contract carries it → The reviewer checks 13.
- No secret in `VITE_*` / `NEXT_PUBLIC_*`, no session token in `localStorage`; user text never reaches
  `dangerouslySetInnerHTML` outside the one sanitizer → The reviewer checks 15.
- Tests render through `renderWithProviders`, mock the network with MSW, never the component's own modules
  → The reviewer checks 16.

## The machine checks — keep them green

| Rule | Lint |
|---|---|
| rendering is pure: no request, no outside change, no ref write, no `setState` during render | the hooks plugin's purity, ref, render-time-state, immutability and globals rules (its `recommended` set) |
| no `setState` inside an effect to mirror other state | the hooks plugin's set-state-in-effect rule |
| hooks rules and complete effect dependencies; wanting to disable the dependencies rule means the effect is wrong | the hooks plugin's rules-of-hooks and exhaustive-deps rules |
| no component defined inside a component | the hooks plugin's static-components rule |
| a list key is a stable id from the data, not the index | the React lint's index-key rule |
| no `fetch` or API client outside the data layer (`shared/api`, `features/*/api.ts`) | `no-restricted-imports`, `no-restricted-globals` |
| no regex literal in a component — a format comes from the rules module | `no-restricted-syntax` |
| no `dangerouslySetInnerHTML` outside the one sanitizer module | the React lint's DOM rule against it, switched off only in that module |
| a function over 80 lines, a file over 500 — split | `max-lines-per-function`, `max-lines` |
| tests query by role and label, use `userEvent`, `findBy*` instead of `waitFor`, no `container` or node access | the Testing Library lint plugin's rules |

Rule ids differ between plugin majors, so the table names each rule by what it checks and the plugin that checks it
(ids that change with a version would make it lie after an update); the exact ids per plugin major are in
`frontend/references/version-checks.md` → React major.

## The reviewer checks — the machine cannot

1. **Do not store what you can compute.** A value derived from props or state is computed during render; state
   holds only what the user or the server gave.
2. **An effect synchronizes with an outside system** (a subscription, the DOM, a widget outside React) — never
   reacts to its own state. What a user did is handled in the event handler.
3. **Server data only through the data layer**: one hook per read `operationId` (TanStack Query), a mutation per
   write; the component never fetches. A reference list (a dictionary) has one hook, shared by every screen.
4. **After a successful mutation the read queries whose data it changed are refreshed**: invalidated
   (`invalidateQueries` by the query key of each affected read `operationId`) or fed the response through
   `setQueryData`. The keys are the list the item belongs to and the item itself; the dictionaries only when the
   write changes one. A screen that keeps showing the old list after a write is the most common data-layer defect,
   and a page reload is not the fix — the user must never need it.
5. **Server data is not copied into `useState`** — except a form's initial values, reset with `key`.
6. **State is minimal and grouped**: related values are one union object (`typescript` → «Impossible states are
   unrepresentable») or a `useReducer`. More than four or five `useState` in a component is a sign it does two
   jobs.
7. **A page is a data hook `use<Screen>()` plus a view** (props in, JSX out); the view knows nothing of the API.
8. **Reset state with `key`**, not with an effect watching a prop.
9. **`useRef` holds a DOM node or a value that does not affect what is shown.**
10. **Memoize only on a measurement** (the Profiler) or when the value is an effect's dependency; with the React
    Compiler on, do not memoize by hand.
11. **Shared logic with hooks is a custom `use*` hook**, never a copy; shared Loading / Error / Empty are
    components, chosen by the query's status.
12. **A form is one library (React Hook Form) and one schema derived from the generated request type**; a format
    rule is imported from the one module the domain model's «Кто ещё применяет» names; field values are not
    mirrored in `useState`.
13. **What the user may do** (a button shown or not) **comes from the response** when the contract carries it,
    never re-derived on the screen.
14. **Variants by composition** (`children`, a separate component), not by yet another boolean prop. Context holds
    what rarely changes (session, theme), never server data.
15. **The browser keeps no secret and no session token.** Text a user typed, or another user wrote, never reaches
    `dangerouslySetInnerHTML`; rich text the product must show goes through one sanitizer (DOMPurify) in one
    module, and a link built from such text gets its scheme checked (`https:` / `mailto:` only). A `VITE_*` or
    `NEXT_PUBLIC_*` variable is shipped to every visitor — an API key or a secret never goes there; a call that
    needs one goes through the backend. A session token never goes into `localStorage` or `sessionStorage`; how
    the session travels is the architecture §1 decision — the API's `HttpOnly` cookie (credentials sent), or a
    Bearer token, the backend skills' default, held in memory only.
16. **Tests**: Testing Library through `renderWithProviders` from the shared test folder, the network mocked by
    MSW, the component's own hooks and modules never mocked, one behaviour per test (`vitest`).

React-version facts (`ref` as an ordinary prop, `<Context>` as its own provider) are points to check:
`frontend/references/version-checks.md` → React major.
