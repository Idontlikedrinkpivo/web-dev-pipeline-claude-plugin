---
name: docs-site
description: >-
  Builds the project's documentation/ into one static site to read and share: navigation by
  section (requirements, data, API, architecture, interface, deploy, operations), search, and cross-links — every
  FR, NFR, BR, UC, TC and screen number links to where it is defined, an operationId to the API page; diagrams
  shown in place; the API contract as an interactive page. Committed in documentation/_site; opened in the
  built-in browser through a local server, or from disk in any browser. Use when the user asks for a
  documentation site, «собери сайт документации», «открой документацию», «выгрузи документы в HTML», «опубликуй
  документацию», or wants the documents as pages instead of Markdown. Not for writing or fixing documents, and
  not the progress page (that one rebuilds itself — pipeline → progress-files).
---

# Documentation site

The documents stay Markdown — agents write them, git reviews them, the checks parse them. The site is a view
built from them: what a manager, an analyst or an operator opens in a browser, with links where the Markdown
only has numbers.

## Steps

1. **Build** from the project root — everything in `documentation/` except `plans/` (Node is needed only for the
   API page; without it the API section is a table of operations):

   ```bash
   python3 "${CLAUDE_SKILL_DIR}/scripts/build_site.py"
   ```

   The site goes to `documentation/_site/` and is **committed** (`docs: сайт документации`), so whoever
   clones the repository opens it without building. A rebuild over unchanged documents changes no file, and an
   edited document changes its own page, the navigation and the search index — commit only when `git status`
   shows a change.
2. **Read the report** the script prints: pages, ids per kind, ids mentioned but never defined, broken links.
   An id that is mentioned and defined nowhere, or a broken link between documents, is a defect of the
   documents, not of the site: name each in the close. Do not edit a document to make the site prettier.
3. **Open it and look at it.** In the desktop app the built-in browser shows a page given as a file without its
   stylesheet and scripts — no menu, no search — so serve the site:
   `python3 "${CLAUDE_SKILL_DIR}/scripts/site_server.py"` prints `http://127.0.0.1:<port>/index.html` (it reuses
   a server already running for this site). Open that address in the built-in browser yourself and give it as
   a link in the chat — that link is the user's one click back to the site. Without a built-in browser (a
   terminal), give `open documentation/_site/index.html`: the user's own browser shows the file whole. Never
   point at the file in the file tree — it shows the HTML source. Then check it: follow one requirement link,
   one test-case link and the API page, try the search with one number. A page that renders wrong — a table that broke, a diagram missing — is a fix in
   `scripts/mdhtml.py`, reported, not hidden.
4. **Close** with one line: the site's link from step 3, pages and ids, and what the report
   found. Publishing (GitHub Pages, a server, a zip) is the user's step — the site holds
   the project's whole documentation, so it leaves the machine only on their word.

**Kept fresh.** Once a project has a site, the plugin's hook rebuilds it in the background after every edit
of a document under `documentation/` (`plans/` and the site itself left out), a subagent's included —
`scripts/rebuild.py`: one build at a time, a burst of edits costs two builds, the API page rebuilt only when
`documentation/api/` changed. **A commit that includes documents first waits for that rebuild**
(`python3 "${CLAUDE_SKILL_DIR}/scripts/rebuild.py" . --wait`) **and stages `documentation/_site` with them**, so
every commit holds the site of its own documents. A project without a site gets none until someone asks.

**«Открой документацию»** with a site already built: step 3 alone. Stop the server when the user is done with
the site (`site_server.py --stop`); the iteration's close stops it too.

`documentation/_site/` is generated: never edit it, and never read it as a source — documents, checks and
searches work on the Markdown (`doc-versioning` → Registry).

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
