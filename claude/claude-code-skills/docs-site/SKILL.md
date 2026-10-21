---
name: docs-site
description: >-
  Builds the project's documentation/ into one static site to read, hand to a customer or publish: navigation by
  section (requirements, data, API, architecture, interface, deploy, operations), search, and cross-links — every
  FR, NFR, BR, UC, TC and screen number links to where it is defined, an operationId to the API page; diagrams
  shown in place; the API contract as an interactive page. Opens from disk, no server. Use when the user asks for
  a documentation site, «собери сайт документации», «покажи документацию заказчику», «выгрузи документы в HTML»,
  «опубликуй документацию», or wants the documents as pages instead of Markdown. Not for writing or fixing
  documents, and not the progress page (that one rebuilds itself — pipeline → progress-files).
---

# Documentation site

The documents stay Markdown — agents write them, git reviews them, the checks parse them. The site is a view
built from them: what a customer, a manager or an operator opens in a browser, with links where the Markdown
only has numbers.

## Steps

1. **Who reads it.** Ask once, unless the request says:
   - A. Команда — everything in `documentation/` except `plans/`.
   - B. Заказчик — the same without open questions, interface wishes and the project map
     (`--audience customer`).
2. **Build** from the project root (Node is needed only for the API page; without it the API section is a
   table of operations):

   ```bash
   python3 "${CLAUDE_SKILL_DIR}/scripts/build_site.py" --out site [--audience customer]
   ```

   The output goes to `site/`; add `site/` to `.gitignore` when it is not there — the site is rebuilt, never
   committed. For a hand-over, build into the release folder instead:
   `--out release/<version>/docs` (beside `DEPLOY.md`).
3. **Read the report** the script prints: pages, ids per kind, ids mentioned but never defined, broken links.
   An id that is mentioned and defined nowhere, or a broken link between documents, is a defect of the
   documents, not of the site: name each in the close. Do not edit a document to make the site prettier.
4. **Look at it** before handing it over: open `site/index.html` (in the browser pane, or tell the user to
   open it from disk), follow one requirement link, one test-case link and the API page, try the search with
   one number. A page that renders wrong — a table that broke, a diagram missing — is a fix in
   `scripts/mdhtml.py`, reported, not hidden.
5. **Close** with one line: the link to `site/index.html`, pages and ids, the audience, and what the report
   found. Publishing (GitHub Pages, a server, a zip for the customer) is the user's step — the site holds
   the project's whole documentation, so it leaves the machine only on their word.

## What the site does

- **Navigation** by `documentation/` top folders in the pipeline's order; within a section, by path.
- **Cross-links.** An id is defined where it first appears as a table row's first cell, a heading
  («### UC-4. …»), a bold paragraph start («**З-2. …**») or a screen-spec file name (`S-3-card.md`); every
  other mention links there. Query and procedure ids (`З-`, `П-`) link only inside the operations document.
  `` `bookRoom` `` links to its operation on the API page; `` `../db/schema.md` `` to that page.
- **Search** over titles and text, and straight to a definition when the query is a number.
- **Light and dark** follow the system; narrow screens get a menu button; print drops the chrome.

## References

- `scripts/build_site.py` — the builder; `scripts/mdhtml.py` — the Markdown converter it shares with the
  progress page; `assets/site.css`, `assets/site.js` — the look and the search.
