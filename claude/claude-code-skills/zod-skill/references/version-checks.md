# Zod — version-sensitive points

Facts that change between releases. The skill deliberately gives no answer here, because the answer depends on the
installed version: read it from the lockfile, then check the point — `work` does it once per run through Context7
(`work/references/context7.md`) and pastes the answers into the packet's `CURRENT LIB DOCS`; elsewhere, Context7 or
a quick probe in the project.

- **Major line and import path** (`zod`, a versioned subpath, the mini build): string formats, enums, object
  strictness helpers, error-customisation params and error formatters differ between majors.
- **Cross-field refinements on an object:** whether the parent check still runs when some fields failed, and with
  what data.
- **Defaults, prefaults and catch:** whether the default is validated or transformed, and when.
- **String → boolean/number for env and query params:** which strings a helper accepts, versus what a generic
  coerce does (a coerced `"false"` may be truthy).
- **Optional vs explicit `undefined`** under `exactOptionalPropertyTypes`, and what the output type says about it.
- **Date/ISO and URL helpers:** string format or codec, offsets accepted, schemes and hosts accepted.
- **Parse options and global config:** the raw-input-in-issues option, error maps and their timing.
- **JSON Schema output:** how the installed line converts a schema to JSON Schema (built in or a separate package),
  and how nullable, integer bounds and string formats come out — what the contract test compares.
