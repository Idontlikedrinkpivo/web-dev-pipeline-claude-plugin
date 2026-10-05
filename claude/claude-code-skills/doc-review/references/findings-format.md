# Findings format

The reviewer's last message is this labelled text and nothing else — no
preamble, no summary after it. Field names are fixed: synthesis reads them by
name.

```
reviewer: <persona name, e.g. coherence-reviewer>

finding: 1
title: <short, specific, 10 words or fewer>
severity: P0 | P1 | P2 | P3
section: <document section where the issue appears>
finding_type: error | omission
autofix_class: safe_auto | gated_auto | manual
confidence: 50 | 75 | 100
why_it_matters: <what goes wrong if it stays — not a restatement of the issue>
suggested_fix: <the fix, or: none>
evidence:
- "<quote from the document or the repo>"
- "<another quote, optional>"

finding: 2
...

residual_risks:
- <a risk you checked and could not turn into a finding, or: none>

deferred_questions:
- <a question for the author, or: none>
```

With nothing to report, the whole message is:

```
reviewer: <persona name>
findings: none
residual_risks:
- none
deferred_questions:
- none
```

Field meanings:

- `severity` — `P0` must fix, `P1` should fix, `P2` could fix, `P3` low signal.
  Never "high" / "medium" / "low".
- `finding_type` — `error` (the text says something wrong) or `omission`
  (something required is missing).
- `autofix_class` — `safe_auto` = one correct fix, applied silently;
  `gated_auto` = a concrete fix the user confirms; `manual` = a judgment call.
- `confidence` — only `50`, `75`, or `100` (anchors in the reviewer packet).
- `evidence` — at least one quoted line.
