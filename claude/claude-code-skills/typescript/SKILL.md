---
name: typescript
description: >-
  Internal: TypeScript rules (typed errors, exhaustive switch, no any); read by work's executors and reviewers before
  .ts/.tsx code.
---

# TypeScript

The model knows TypeScript; these are the places where code an agent writes goes wrong anyway — they are what an
audit of a real project found. A rule a machine checks is one line here with its lint rule; the config is
`repo-scaffold/references/quality-gates.md`. Examples «так / не так»: `references/examples.md`.

## The machine checks — keep them green, never disable one without a reason in the comment

| Rule | Lint / compiler |
|---|---|
| strict mode plus `noUncheckedIndexedAccess`, `noImplicitOverride`, `noImplicitReturns`, `noFallthroughCasesInSwitch`, `verbatimModuleSyntax`; the tests are type-checked too | `tsconfig`, `typecheck` |
| no `any`; outside data is `unknown` and parsed by a schema at the boundary | `no-explicit-any`, `no-unsafe-*` |
| no `as` on outside data, no `as unknown as`, no `!` | `no-unsafe-type-assertion`, `no-non-null-assertion` |
| an error class is never empty — it carries a `readonly kind` | `no-restricted-syntax` (empty subclass) |
| a union of errors or statuses is handled in an exhaustive `switch` with `assertNever` | `switch-exhaustiveness-check` |
| an error made in a `catch` passes the caught one: `{ cause: e }`; a `catch` always names its variable | `preserve-caught-error` (`requireCatchParameter`; the project's error classes in `errorClassNames` — check the installed ESLint has that option, `repo-scaffold/references/quality-gates.md`) |
| no empty `catch`, not even with a comment inside | `no-empty`, `no-restricted-syntax` (empty catch block) |
| throw and reject only `Error` and its subclasses; a `catch` variable is `unknown` and narrowed first | `only-throw-error`, `prefer-promise-reject-errors`, `use-unknown-in-catch-callback-variable` |
| every promise is awaited or explicitly `void`ed with a reason | `no-floating-promises` |
| no async function where a sync one is expected (`onClick`, `forEach`, `setTimeout`) | `no-misused-promises` |
| `return await` inside `try` | `return-await` (`in-try-catch`) |
| a closed set is a string union or an `as const` object, not an `enum` | `no-restricted-syntax` (`TSEnumDeclaration`), or `erasableSyntaxOnly` where Node runs the `.ts` files directly |
| no condition the type already decides | `no-unnecessary-condition` |
| a disabled rule names its reason, never a file-wide disable | `eslint-comments/require-description`, `no-unlimited-disable` |

## The reviewer checks — the machine cannot

1. **Every named error is its own type with a literal `kind`; an operation's expected failures are a union of
   them.** Empty classes are identical to the compiler, so a missed branch passes as success — the audit's new
   error answered 204. A failure of an outside call keeps its cause and its operation. The lint checks the cause
   only for the classes listed in `errorClassNames`: a new error class made in a `catch` joins that list. A plain
   name there means the constructor takes the options object (`{ cause }`) second, as `Error` does — keep that
   shape (`new InvalidCursor("shape", { cause: e })`); a class that takes it elsewhere is listed as
   `{ name, argumentPosition }` (1-based), or the lint reports correct code.
2. **One translation of failures to answers**, in one module, as a `switch (e.kind)` with `assertNever` — never
   a mapper per route. A table of codes is `satisfies Record<ErrorKind, number>`, so a new kind breaks the build.
3. **A failure the user only sees as a generic answer writes one log line** with the cause's name, never secrets,
   keys or addresses.
4. **Impossible states are unrepresentable**: `{status: "loading"} | {status: "error", error} | {status: "ready",
   data}`, not `isLoading`, `error?`, `data?` side by side.
5. **Narrowing is real**: by `kind`, `in`, `typeof`, or a type guard `x is T` whose body actually checks — a lying
   guard is worse than a cast.
6. **Independent awaits run together** (`Promise.all`); a sequence is a sequence only when one needs the other.
7. **Ids of different things are different types** (a brand or a value object): a user id is not an email — the
   audit found a creator matched by email on one side and by id on the other.
8. **Domain values are `readonly`; a function does not change its arguments.**
9. **One rule, one module.** A format, a status list, a length limit is imported from its owner — the domain
   model's «Кто ещё применяет» names it. A second regex or literal of the same rule is a finding even when it
   matches today: copies drift.
10. **A shared step lives in a module of shared steps**, never imported from another use case's file.

Python has the same rules in its own words: `python`.
