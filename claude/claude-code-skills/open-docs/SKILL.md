---
name: open-docs
description: >-
  Opens the project's documentation site in the built-in browser and gives its link, building it first when there is
  none; stops its local server on request. Use for «открой сайт», «открой документацию», «дай ссылку на сайт», «закрой
  сайт». Building or publishing the site is `docs-site`.
---

# Open the documentation site

The site lives in `documentation/_web-docs/` and the plugin keeps it fresh by itself (`docs-site` → Built at the
first document, kept fresh after). This command only shows it.

## Open

From the project's root:

1. **Wait for a rebuild in flight**, so the page is not a version behind:
   `python3 "${CLAUDE_SKILL_DIR}/../docs-site/scripts/rebuild.py" . --wait`.
2. **No site yet** (`documentation/_web-docs/index.html` missing): build it —
   `python3 "${CLAUDE_SKILL_DIR}/../docs-site/scripts/build_site.py"`. Say in one line that it was built now and
   goes into git with the next documents' commit (`docs-site` → step 1). No `documentation/` at all: say there
   is nothing to show yet and stop.
3. **Serve and open**: `python3 "${CLAUDE_SKILL_DIR}/../docs-site/scripts/site_server.py"` prints
   `http://127.0.0.1:<port>/index.html` and reuses a server already running for this site. Open that address in
   the built-in browser yourself — the built-in browser shows a page given as a file without its menu and
   search, so never open the file — and give the address as a link in the chat: the user's one click back. A
   page that was open before may show an older copy: reload it.
4. Without a built-in browser (a terminal): give `open documentation/_web-docs/index.html` instead — any ordinary
   browser shows the file whole.

Answer in one line: the link, and «собран сейчас» when step 2 ran. Nothing else — no report, no checks; those
are `docs-site`.

## Stop

«Закрой сайт», «останови сайт»: `python3 "${CLAUDE_SKILL_DIR}/../docs-site/scripts/site_server.py" --stop`, and
one line that the link no longer opens until the next «открой сайт». The iteration's close stops it too.
