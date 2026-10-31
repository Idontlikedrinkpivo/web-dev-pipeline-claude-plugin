# Who applies what

Read when deciding whether a `UX-<n>` rule is yours to apply or only to check.

| Reader | Applies |
|---|---|
| `ui-design` | records the product type and the visual direction, decides the screen set, and runs Полнота макета against it before and after drawing; picks no widget itself — it hands the choices to the builders |
| `figma-opus` / `figma-sonnet` (or a designer) | pick every widget, presentation and behaviour pattern — button or menu item, dropdown or radio group, dialog or side panel or page, toast or banner, table or cards, undo or confirmation — compose frames that satisfy Sections 1–7 and 9 and Полнота макета by the taste rules of `frontend-design`, and write the copy by UX-12, UX-21, UX-78 and UX-79 into the «Тексты» table; a designer may choose differently without touching any document |
| `screen-spec` | records what the frames chose — the behaviour each element has, its texts verbatim from «Тексты», cited by frame — and the `UX-<n>` exception a frame notes; it never picks a widget or rewrites a text |
| `frontend` | implements Sections 1–9 — the look from the frames and the code rules of Section 1 (UX-59, UX-61, UX-62, UX-66), the behaviour (Sections 2–7), the implementation rules (Section 8, with the code-level detail in `web-design-guidelines`), the texts (Section 9) — and the accessibility baseline; its executor `impl-ui` runs Проверка экрана перед сдачей before handing a screen unit over |
| `doc-review` (design lens), `code-review-unit` (UI lens) | cite the `UX-<n>` a finding breaks; the UI lens also checks Section 8 against `web-design-guidelines` and the screen checklist |
| `ui-test-cases` (run) | checks the screen-checklist items a screenshot shows when it compares a screen with its frame |
