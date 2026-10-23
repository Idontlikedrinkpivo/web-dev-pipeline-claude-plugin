---
name: open-docs
description: >-
  Opens the documentation site in the built-in browser, building it if missing, and gives its link; stops it on
  request. Use for «открой документацию», «дай ссылку на сайт», «закрой сайт». Building is docs-site.
---

# Open the documentation site

The site lives in `documentation/_web-docs/` and the plugin keeps it fresh by itself (`docs-site` → Built at the
first document, kept fresh after). This command only shows it.

## Open

From the project's root:

1. **Wait for a rebuild in flight**, so the page is not a version behind:
   `python3 "${CLAUDE_SKILL_DIR}/../docs-site/scripts/rebuild.py" . --wait`.
2. **No site yet** (`documentation/_web-docs/index.html` missing): build it through the rebuild queue, never
   `build_site.py` beside it (`docs-site` → step 1) —
   `python3 "${CLAUDE_SKILL_DIR}/../docs-site/scripts/rebuild.py" . --api --force`, then
   `python3 "${CLAUDE_SKILL_DIR}/../docs-site/scripts/rebuild.py" . --wait`. Say in one line that it was built now and
   goes into git with the next documents' commit. No `documentation/` at all: say there
   is nothing to show yet and stop.
3. **Serve and open**: `python3 "${CLAUDE_SKILL_DIR}/../docs-site/scripts/site_server.py"` prints
   `http://127.0.0.1:<port>/index.html` and reuses a server already running for this site. Open that address in
   the built-in browser yourself — the built-in browser shows a page given as a file without its menu and
   search, so never open the file — and give the address as a link in the chat: the user's one click back. A
   page that was open before may show an older copy: reload it.
4. Without a built-in browser (a terminal): open the file in the user's own browser yourself — `open
   documentation/_web-docs/index.html` on macOS, `xdg-open documentation/_web-docs/index.html` on Linux (`uname`
   tells which) — and give its full path as the link; where neither command exists, the full path alone. Any
   ordinary browser shows the file whole.

Answer in one line: the link, and «собран сейчас» when step 2 ran. Nothing else — no report, no checks; those
are `docs-site`.

## Stop

«Закрой сайт», «останови сайт»: `python3 "${CLAUDE_SKILL_DIR}/../docs-site/scripts/site_server.py" --stop`, and
one line that the link no longer opens until the next «открой сайт». The iteration's close stops it too.
