---
name: react
description: >-
  React rules an agent breaks by default: no state that can be computed, effects only for outside systems, server
  data only through the data layer, a page split into a data hook and its view, minimal grouped state, forms from
  one schema and one rules module, tests through Testing Library. Most are lint rules (react-hooks v7,
  testing-library, restricted imports — `repo-scaffold/references/quality-gates.md`); the rest are what a reviewer
  checks. Loaded by `work` for every unit touching React files and by `code-review-unit` for its review; use
  whenever React components, hooks or their tests are written, reviewed or refactored. Not what to build from a
  screen spec (`frontend`), accessibility and markup (`web-design-guidelines`) or TypeScript itself (`typescript`).
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
| a list key is a stable id from the data, not the index | `no-array-index-key` |
| no `fetch` or API client outside the data layer (`shared/api`, `features/*/api.ts`) | `no-restricted-imports`, `no-restricted-globals` |
| no regex literal in a component — a format comes from the rules module | `no-restricted-syntax` |
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
5. **State is minimal and grouped**: related values are one union object (`typescript` rule 4) or a `useReducer`.
   More than four or five `useState` in a component is a sign it does two jobs.
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
14. **Tests**: Testing Library through `renderWithProviders` from the shared test folder, the network mocked by
    MSW, the component's own hooks and modules never mocked, one behaviour per test (`vitest`).

React 19: `ref` is an ordinary prop (no `forwardRef`), `<Context>` is its own provider. Check the installed
version before relying on either.
