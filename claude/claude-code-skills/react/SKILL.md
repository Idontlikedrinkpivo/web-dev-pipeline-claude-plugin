---
name: react
description: >-
  Internal: React rules (derived state, effects only for outside systems, data hooks); read by work's executors before
  React code.
---

# React

`frontend` says what a screen must do; this skill says how its React code stays changeable. The rules come from
react.dev (Rules of React, You Might Not Need an Effect, Choosing the State Structure) and from what an audit of a
real project found: a page of 687 lines with 19 `useState`, 17 `useRef` and 8 `useEffect`, network calls in
components, a dictionary loaded four ways. Examples «так / не так»: `references/examples.md`.

## The machine checks — keep them green

| Rule | Lint |
|---|---|
| rendering is pure: no request, no outside change, no ref write, no `setState` during render | react-hooks v7 `recommended`: `purity`, `refs`, `set-state-in-render`, `immutability`, `globals` |
| no `setState` inside an effect to mirror other state | `set-state-in-effect` |
| hooks rules and complete effect dependencies; wanting to disable `exhaustive-deps` means the effect is wrong | `rules-of-hooks`, `exhaustive-deps` |
| no component defined inside a component | `static-components` |
| a list key is a stable id from the data, not the index | `@eslint-react/no-array-index-key` |
| no `fetch` or API client outside the data layer (`shared/api`, `features/*/api.ts`) | `no-restricted-imports`, `no-restricted-globals` |
| no regex literal in a component — a format comes from the rules module | `no-restricted-syntax` |
| no `dangerouslySetInnerHTML` outside the one sanitizer module | the `@eslint-react` DOM rule against it (its name per the installed version), switched off only in that module |
| a function over 80 lines, a file over 500 — split | `max-lines-per-function`, `max-lines` |
| tests query by role and label, use `userEvent`, `findBy*` instead of `waitFor`, no `container` or node access | `testing-library/*` |

## The reviewer checks — the machine cannot

1. **Do not store what you can compute.** A value derived from props or state is computed during render; state
   holds only what the user or the server gave.
2. **An effect synchronizes with an outside system** (a subscription, the DOM, a widget outside React) — never
   reacts to its own state. What a user did is handled in the event handler.
3. **Server data only through the data layer**: one hook per read `operationId` (TanStack Query), a mutation per
   write; the component never fetches. A dictionary has one hook, `useDictionary(name)`.
4. **Server data is not copied into `useState`** — except a form's initial values, reset with `key`.
5. **State is minimal and grouped**: related values are one union object (`typescript` → «Impossible states are
   unrepresentable») or a `useReducer`. More than four or five `useState` in a component is a sign it does two
   jobs.
6. **A page is a data hook `use<Screen>()` plus a view** (props in, JSX out); the view knows nothing of the API.
7. **Reset state with `key`**, not with an effect watching a prop.
8. **`useRef` holds a DOM node or a value that does not affect what is shown.**
9. **Memoize only on a measurement** (the Profiler) or when the value is an effect's dependency; with the React
   Compiler on, do not memoize by hand.
10. **Shared logic with hooks is a custom `use*` hook**, never a copy; shared Loading / Error / Empty are
    components, chosen by the query's status.
11. **A form is one library (React Hook Form) and one schema derived from the generated request type**; a format
    rule is imported from the one module the domain model's «Кто ещё применяет» names; field values are not
    mirrored in `useState`.
12. **What the user may do** (a button shown or not) **comes from the response** when the contract carries it,
    never re-derived on the screen.
13. **Variants by composition** (`children`, a separate component), not by yet another boolean prop. Context holds
    what rarely changes (session, theme), never server data.
14. **The browser keeps no secret and no session token.** Text a user typed, or another user wrote, never reaches
    `dangerouslySetInnerHTML`; rich text the product must show goes through one sanitizer (DOMPurify) in one
    module, and a link built from such text gets its scheme checked (`https:` / `mailto:` only). A `VITE_*` or
    `NEXT_PUBLIC_*` variable is shipped to every visitor — an API key or a secret never goes there; a call that
    needs one goes through the backend. A session token never goes into `localStorage` or `sessionStorage`; how
    the session travels is the architecture §1 decision — the API's `HttpOnly` cookie (credentials sent), or a
    Bearer token, the backend skills' default, held in memory only.
15. **Tests**: Testing Library through `renderWithProviders` from the shared test folder, the network mocked by
    MSW, the component's own hooks and modules never mocked, one behaviour per test (`vitest`).

React 19: `ref` is an ordinary prop (no `forwardRef`), `<Context>` is its own provider. Check the installed
version before relying on either.
