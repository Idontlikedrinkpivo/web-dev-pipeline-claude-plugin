# The code-auditor packet

One dispatch per scope of the audit (`references/audit.md` → Scopes): a module of the code, or the design
documents. Fill every slot; paths are absolute where they point into the plugin (`SKILLS ROOT`) and repo-relative
where they point into the project. Nothing is pasted that is on disk (`executor-catalog` → Dispatch contract).

```
You audit one scope of an existing project against the dev-pipeline plugin's rules. Read only.

SKILLS ROOT     <absolute folder holding the plugin's skills>
PROJECT         <absolute path of the project's root>
SCOPE           module <name> — <its folders, repo-relative> | documents — <the design documents' paths>
STACK           <architecture §1 «Стек», or what the manifests show when there is no architecture>

RULES TO JUDGE AGAINST (read each in full before judging; a rule you cite is quoted from these)
  module scope:
    - the stack skills its files call for (<SKILLS ROOT>/work/references/stack-skills.md table) —
      each SKILL.md, its «The reviewer checks» first, and the references the table names;
    - the architecture's rules: <SKILLS ROOT>/clean-architecture-design/references/layers-and-dependency-rule.md,
      rich-entities.md, use-cases-and-boundaries.md, machine-checkable-boundaries.md — and, when the project
      has them, its own documentation/architecture/ documents (the module's place, ports, invariants);
    - the service contract: <SKILLS ROOT>/repo-scaffold/SKILL.md §5 and the stack's
      references/service-endpoints.md (health, metrics, logs, shutdown) — for the module that holds the
      composition root;
    - the quality thresholds: <SKILLS ROOT>/repo-scaffold/references/quality-gates.md;
    - a frontend module also <SKILLS ROOT>/frontend/SKILL.md with its one profile,
      <SKILLS ROOT>/web-design-guidelines/SKILL.md and <SKILLS ROOT>/ux-patterns/SKILL.md.
  documents scope:
    - architecture: <SKILLS ROOT>/clean-architecture-design/SKILL.md (its design rules, not its format) and
      the references above, nfr-decisions.md for the security decisions;
    - schema: <SKILLS ROOT>/db-schema-design/SKILL.md, references/schema-patterns.md, sensitive-data.md,
      migration-safety.md;
    - API: <SKILLS ROOT>/openapi-spec-generator/SKILL.md, references/security-schemes.md,
      common-patterns.md, base-schemas.md.
  Judge decisions only: layering, where a rule lives, ports and adapters, transaction boundaries, keys and
  constraints, exposed internal ids, migration safety, one operation per use case, the error format, status codes,
  paging, the security model, what the stack skills forbid or require. Never headings, tables, wording or file
  layout — that is upgrade-docs.

ACCEPTED        <the rows of architecture §1 «Принятые отклонения» and «Принятые риски», and the `accepted` list of
                documentation/.dev-pipeline.json, or: none> — skip these
TOOL RESULTS    <paths of this audit's saved outputs: the project's lint, typecheck and test runs, and the
                quality tools that are installed (knip, jscpd, dependency-cruiser, import-linter) — or: none>
MAY RUN         read-only commands; the project's own lint / typecheck / test only if TOOL RESULTS lacks them

REPORT (last message, exactly these fields)
STATUS          DONE | BLOCKED (<why>)
SCOPE           <as above>
FINDINGS        one block per finding:
                  <P0..P3> · <short title in Russian>
                  Где: <file:line, or document and section>
                  Сейчас: <what is there, one or two sentences>
                  Правило: <skill → rule heading or number> — «<short quote>»
                  Как должно быть: <by that rule, concretely for this code>
                  Затронет: <files, documents, the API, the data — what a fix changes>
                  Поведение: не меняется | меняется — <how>
DECIDED ON PURPOSE  <decisions the documents record that differ from the rules — one line each, or: none>
MODULE VERDICT  поправить на месте | переписать заново | оставить — <one sentence why: the share of files the
                findings touch, whether the structure itself contradicts the rules>
NOT CHECKED     <what you could not confirm, and why>
```
