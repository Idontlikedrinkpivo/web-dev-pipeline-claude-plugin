# Embedded copy: what changed against the original

- **Original:** Vercel Web Interface Guidelines,
  https://github.com/vercel-labs/web-interface-guidelines, file
  `command.md`, commit `434b7f9` (5 October 2026). The skill wrapper of the
  original (`vercel-labs/agent-skills`, `skills/web-design-guidelines`)
  fetches that file from GitHub on every run; this copy carries the rules
  itself.
- **Licence:** MIT, `LICENSE` in this folder. The changes below are
  distributed under the same licence.
- **Why the changes:** the rules are the code-level form of `ux-patterns`.
  A rule that disagreed with it was rewritten to agree, by the decisions of
  the reconciliation (Р1–Р22); the mapping of every rule is in the plugin
  repository, `claude/ux-sources/сверка.md`, appendix Б.

## Changed

- Every rule ends with the `ux-patterns` rule it belongs to (`→ UX-n`).
- Rewritten to agree with `ux-patterns`:
  - async updates — polite announcements for toasts and field messages,
    `aria-describedby` for a field error, `role="alert"` only for a failed
    operation (Р10, UX-28);
  - focus after a failed submit — the error summary, a one-field form keeps
    focus on the field (Р11, UX-22);
  - placeholders — none except in a search field; a format example goes in
    the hint between the label and the field (Р9, UX-17, UX-19);
  - the submit button — a busy state without `disabled` during the request
    (UX-15);
  - curly quotes → «ёлочки» and „лапки“; Title Case → a capital only on the
    first word (Р20, UX-78, UX-12);
  - second person → «вы» in lower case and section names without pronouns
    (Р21, UX-79);
  - reduced motion also turns off smooth scrolling (Р19, UX-61);
  - input types — `inputmode` instead of `type="number"`, which is also an
    anti-pattern now (UX-19); a visible label, not `aria-label` alone
    (UX-17); truncation only for secondary text (UX-71); fonts load with
    the `cyrillic` subset (UX-59);
  - the copy examples are in Russian.
- The language rule (`Accept-Language`, not IP) is marked «только по
  требованиям»: it matters only for a multilingual product.
- Hydration rules are marked Next.js only and point to `frontend` →
  `references/nextjs.md`.
- The output format names the rule: `file:line — UX-n — суть`, in
  Russian.

## Removed

- «`&` over "and" where space-constrained» — a norm of English text.
- Fetching the rules from the network.

## Updating from the original

Diff the new `command.md` against commit `434b7f9`, give each new rule its
`UX-n` (a rule with no home goes into `ux-patterns` first), rewrite one that
disagrees, then update the commit at the top of this file.
