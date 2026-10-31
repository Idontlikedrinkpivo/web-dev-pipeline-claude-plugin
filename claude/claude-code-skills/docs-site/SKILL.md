---
name: docs-site
description: >-
  Builds documentation/ into a static HTML site with menu, search and Swagger. Use for «собери сайт документации»,
  «пересобери сайт», «выгрузи документы в HTML». Hosting: the user; opening: open-docs.
---

# Documentation site

The documents stay Markdown — agents write them, git reviews them, the checks parse them. The site is a view
built from them: what a manager, an analyst or an operator opens in a browser, with links where the Markdown
only has numbers.

## Steps

1. **Build** from the project root — everything in `documentation/` except `plans/` (Node is needed only for the
   API page; without it the API section is a table of operations) — through the same queue the plugin's hook
   uses, then wait for it and print its report:

   ```bash
   python3 "${CLAUDE_SKILL_DIR}/scripts/rebuild.py" . --api --force
   python3 "${CLAUDE_SKILL_DIR}/scripts/rebuild.py" . --wait --report
   ```

   Never `build_site.py` directly: a background rebuild the hook started may be running, and it swaps the
   whole site folder in at its end — a second build beside it loses its output or the folder mid-write.
   `--force` builds even where the hook would not start a first site (another repository's `documentation/`,
   a site the user once declined): the user asked for this one.

   The site goes to `documentation/_web-docs/` and is **committed** (`docs: сайт документации`), so whoever
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
   terminal), open the file in the user's own browser yourself — `open documentation/_web-docs/index.html` on
   macOS, `xdg-open …` on Linux (`uname` tells which) — and give its full path; where neither command exists,
   the full path alone: the user's own browser shows the file whole. Never
   point at the file in the file tree — it shows the HTML source. Then check it: follow one requirement link,
   one test-case link and the API page, try the search with one number. A page that renders wrong — a table that broke, a diagram missing — is a fix in
   `scripts/mdhtml.py`, reported, not hidden.
4. **Close** with one line: the site's link from step 3, pages and ids, and what the report
   found. Publishing (GitHub Pages, a server, a zip) is the user's step — the site holds
   the project's whole documentation, so it leaves the machine only on their word.

**Built at the first document, kept fresh after.** The plugin's hook builds the site in the background as soon
as a pipeline project writes its first document (the brainstorm or the SRS), and rebuilds it after every edit
of a document under `documentation/` (`plans/` and the site itself left out), a subagent's included —
`scripts/rebuild.py`: one build at a time, a burst of edits costs two builds, the API page rebuilt only when
`documentation/api/` changed. **A commit that includes documents first waits for that rebuild**
(`python3 "${CLAUDE_SKILL_DIR}/scripts/rebuild.py" . --wait`) **and stages `documentation/_web-docs` with them**, so
every commit holds the site of its own documents. The commit that first carries the site ends with its link
(step 3), so the user knows it exists. Another repository with a `documentation/` folder gets no site, nor does
a project whose user declined it (`upgrade-docs` → `docs-site` skipped).

**«Открой сайт», «открой документацию»** is the `open-docs` skill (`/dev-pipeline:open-docs`): it waits for a rebuild in
flight, builds a missing site, serves it and opens it — step 3 alone. It also stops the server on «закрой
сайт»; the iteration's close stops it too.

`documentation/_web-docs/` is generated: never edit it, and never read it as a source — documents, checks and
searches work on the Markdown (`doc-versioning` → Registry).

## What the site does

- **Navigation** by `documentation/` top folders in the pipeline's order; within a section, by path.
- **Cross-links.** An id is defined where it first appears as a table row's first cell, a heading
  («### UC-4. …»), a bold paragraph start («**З-2. …**») or a screen-spec file name (`S-3-card.md`); every
  other mention links there. Query and procedure ids (`З-`, `П-`) link only inside the operations document; an architecture
  assumption (`ДП-3`) links to its row in the open questions.
  `` `bookRoom` `` links to its operation on the API page; `` `../db/schema.md` `` to that page.
- **The API page** is Swagger UI over the contract bundled into one JSON (`api/openapi.json`, linked into
  `api/spec.js` with the ids made links): operations by tag,
  request and response schemas and examples, read-only — «Try it out» is off, the site has no API behind it.
  Swagger UI's own files (pinned version) sit in `assets/swagger/`, so the page works offline.
- **What a number means** shows on hover: every linked id carries its definition's text (a requirement row's
  text, a heading's title), on the pages and in the API page's descriptions alike — nobody remembers what
  BR-32 says.
- **Search** over titles and text, and straight to a definition when the query is a number.
- **Light and dark** follow the system; narrow screens get a menu button; print drops the chrome.

## References

- `scripts/build_site.py` — the builder; `scripts/mdhtml.py` — the Markdown converter it shares with the
  progress page; `assets/site.css`, `assets/site.js` — the look and the search.
