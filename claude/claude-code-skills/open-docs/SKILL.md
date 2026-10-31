---
name: open-docs
description: >-
  Opens the documentation site in the built-in browser, building it if missing, and gives its link. Use for «открой
  документацию», «покажи документацию», «закрой сайт». Building: docs-site.
---

# Open the documentation site

The site lives in `documentation/_web-docs/` and the plugin keeps it fresh by itself (`docs-site` → Built at the
first document, kept fresh after). This command only shows it.

## Open

From the project's root:

1. **Wait, and build or rebuild when needed**:
   `python3 "${CLAUDE_SKILL_DIR}/../docs-site/scripts/rebuild.py" . --if-outdated`. It waits for a rebuild in
   flight, so the page is not a version behind; builds a missing site and rebuilds one another plugin version built
   (its new features — a back button, a new page — appear only after a rebuild), both through the rebuild queue,
   never `build_site.py` beside it (`docs-site` → step 1). Its one line says which — «собран сейчас», «пересобран
   для плагина <version>» or «актуален»; give it to the user when the site was built or rebuilt, and that it goes
   into git with the next documents' commit. Exit 1 (no `documentation/` at all): say there is nothing to show yet
   and stop.
2. **Serve and open**: `python3 "${CLAUDE_SKILL_DIR}/../docs-site/scripts/site_server.py"` prints
   `http://127.0.0.1:<port>/index.html` and reuses a server already running for this site. Open that address in
   the built-in browser yourself — the built-in browser shows a page given as a file without its menu and
   search, so never open the file, and never point at it in the file tree, which shows the HTML source — and give
   the address as a link in the chat: the user's one click back. The server forbids caching, so a page already open shows the current site on its next load.
3. Without a built-in browser (a terminal): open the file in the user's own browser yourself — `open
   documentation/_web-docs/index.html` on macOS, `xdg-open documentation/_web-docs/index.html` on Linux (`uname`
   tells which) — and give its full path as the link; where neither command exists, the full path alone. Any
   ordinary browser shows the file whole.

Answer in one line: the link, and step 1's line when it built or rebuilt the site. Nothing else — no report, no checks; those
are `docs-site`.

## Stop

«Закрой сайт», «останови сайт»: `python3 "${CLAUDE_SKILL_DIR}/../docs-site/scripts/site_server.py" --stop`, and
one line that the link no longer opens until the next «открой сайт». The iteration's close stops it too.
