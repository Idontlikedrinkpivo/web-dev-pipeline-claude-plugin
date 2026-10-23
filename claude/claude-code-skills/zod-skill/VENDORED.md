# Vendored

Source: a Zod skill by Anivar Aravind, https://github.com/anivar/zod-skill (MIT, `LICENSE` in this folder), its
version 1.1.0 (Zod baseline ^4.3.0). Upstream commits `8b7c353`…`bb0620d` (2026-08-08) carry that version; which
one was copied was not recorded.

Adapted for this plugin: the house rules are rewritten around the pipeline's architecture (parse once at the
boundary, the use case's own input type, no raw input in logs), the version checklist is kept as «verify against
the installed version» in `references/version-checks.md`, and a section on frontend form rules and «The reviewer checks» are added.
