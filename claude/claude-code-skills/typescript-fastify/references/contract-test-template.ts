/**
 * contract-test-template.ts — the OpenAPI the app builds against documentation/api/openapi.yaml.
 *
 * Place this file at: tests/contract/openapi.contract.test.ts (written once by repo-scaffold;
 * `typescript-fastify` → The contract test). It needs the `yaml` package in devDependencies and no database:
 * building the document runs no route, so `buildServer` gets the test fakes.
 *
 * What fails, per operation the app serves:
 *   - the contract has no operation with that method and path (path parameter names aside);
 *   - a different operationId;
 *   - a different set of statuses (500, 503 and `default` aside — the global handler answers them, not the route);
 *   - a different request body or success-response body: media types, property names, `required`, `type`,
 *     `nullable`, `enum`, string `format`, length / range / item bounds, `pattern`;
 *   - a different query or header parameter: its name, whether it is required, its schema.
 * What does not fail:
 *   - a contract operation the app does not serve yet — logged; the plan builds it;
 *   - descriptions, titles, examples, defaults, error-body schemas (one handler renders them all);
 *   - the forms two generators write differently for the same thing: 3.0 `nullable` vs 3.1 `anyOf [..., null]`,
 *     `$ref` vs inline, `allOf` merged, numeric `format`s, Zod's safe-integer bounds, the 3.0 boolean
 *     `exclusiveMinimum`, a generator's own `pattern` beside a string `format`.
 *
 * A red test is a route that differs from the contract: fix the route, or change the contract first
 * (`openapi-spec-generator`). A generator quirk that is not a contract difference is normalized in `norm` with a
 * comment — never an operation added to NOT_IN_CONTRACT to make the test pass.
 */
import { readFileSync } from "node:fs"
import path from "node:path"
import { fileURLToPath } from "node:url"

import { describe, expect, it } from "vitest"
import { parse as parseYaml } from "yaml"

// Placeholder — the app factory (foundation §5 bootstrap/) and the fakes its tests already use.
import { buildServer } from "../../src/bootstrap/server.js"
import { testDependencies } from "../helpers/test-dependencies.js"

const HERE = path.dirname(fileURLToPath(import.meta.url))
const CONTRACT = path.resolve(HERE, "../../../documentation/api/openapi.yaml") // placeholder: repo root
/** The service routes the contract does not describe on purpose (`repo-scaffold` §5) — `METHOD path` as served. */
const NOT_IN_CONTRACT = new Set(["GET /health/live", "GET /health/ready", "GET /metrics"])

const METHODS = ["get", "put", "post", "delete", "patch"] as const
const IGNORED_STATUSES = new Set(["500", "503", "default"])
const SKIPPED_HEADERS = new Set(["authorization"]) // carried by the security scheme
const COMPARED_KEYS = [
  "format", "enum", "nullable", "minLength", "maxLength", "minimum", "maximum",
  "exclusiveMinimum", "exclusiveMaximum", "minItems", "maxItems", "pattern",
] as const
const NUMBER_FORMATS = new Set(["int32", "int64", "float", "double"])
const SAFE_INTEGER = Number.MAX_SAFE_INTEGER

type JsonObject = Record<string, unknown>

const isObject = (v: unknown): v is JsonObject => typeof v === "object" && v !== null && !Array.isArray(v)
const asObject = (v: unknown): JsonObject => (isObject(v) ? v : {})
const asArray = (v: unknown): readonly unknown[] => (Array.isArray(v) ? v : [])

/** An OpenAPI document whose `$ref`s resolve, across files (the split contract) or inside one object. */
class OpenApiDocument {
  private readonly files = new Map<string, unknown>()

  constructor(readonly root: JsonObject, readonly file?: string) {
    if (file !== undefined) this.files.set(file, root)
  }

  static fromFile(file: string): OpenApiDocument {
    return new OpenApiDocument(asObject(parseYaml(readFileSync(file, "utf8"))), path.resolve(file))
  }

  private load(file: string): unknown {
    if (this.files.has(file)) return this.files.get(file)
    const parsed: unknown = parseYaml(readFileSync(file, "utf8"))
    this.files.set(file, parsed)
    return parsed
  }

  resolve(node: unknown, base: string | undefined): [unknown, string | undefined] {
    for (let hop = 0; hop < 50; hop++) {
      if (!isObject(node) || typeof node.$ref !== "string") return [node, base]
      const [filePart = "", fragment = ""] = node.$ref.split("#")
      if (filePart !== "") {
        if (base === undefined) throw new Error(`file $ref ${node.$ref} in a document without a path`)
        base = path.resolve(path.dirname(base), filePart)
        node = this.load(base)
      } else {
        node = base === undefined ? this.root : this.load(base)
      }
      for (const part of fragment.split("/").filter((p) => p !== "")) {
        node = asObject(node)[part.replaceAll("~1", "/").replaceAll("~0", "~")]
      }
    }
    throw new Error("a $ref chain longer than 50 — a cycle")
  }
}

type Context = { doc: OpenApiDocument; at: string | undefined; depth: number }
const byJson = (a: unknown, b: unknown): number => JSON.stringify(a).localeCompare(JSON.stringify(b))

/** allOf: the parts merged into one object. */
function mergeAllOf(node: JsonObject, cx: Context, out: JsonObject, props: JsonObject, required: Set<string>): void {
  for (const part of asArray(node.allOf)) {
    const merged = norm(cx.doc, part, cx.at, cx.depth + 1)
    Object.assign(props, asObject(merged.properties))
    for (const name of asArray(merged.required)) if (typeof name === "string") required.add(name)
    for (const [key, value] of Object.entries(merged)) if (!(key in out)) out[key] = value
  }
}

/** 3.1 nullable: anyOf [X, {type: null}] → X with nullable; type: [string, "null"] → string with nullable. */
function foldNullable(node: JsonObject, cx: Context, out: JsonObject): void {
  for (const union of ["anyOf", "oneOf"] as const) {
    const members = asArray(node[union]).map((m) => cx.doc.resolve(m, cx.at)[0])
    if (members.length === 0) continue
    const rest = members.filter((m) => !(isObject(m) && m.type === "null" && Object.keys(m).length === 1))
    if (rest.length === 1) Object.assign(out, norm(cx.doc, rest[0], cx.at, cx.depth + 1))
    else out[union] = rest.map((m) => JSON.stringify(norm(cx.doc, m, cx.at, cx.depth + 1))).sort()
    if (rest.length < members.length) out.nullable = true
  }
  const type = node.type
  if (Array.isArray(type)) {
    if (type.includes("null")) out.nullable = true
    const kinds = type.filter((t) => t !== "null").map(String).sort()
    out.type = kinds.length === 1 ? kinds[0] : kinds
  } else if (type !== undefined) {
    out.type = type
  }
}

/** One form for what generators write differently: bounds, numeric formats, Zod's safe-integer bounds. */
function tidy(out: JsonObject): void {
  if (out.enum !== undefined) out.enum = [...asArray(out.enum)].sort(byJson)
  for (const [flag, bound] of [["exclusiveMinimum", "minimum"], ["exclusiveMaximum", "maximum"]] as const) {
    if (out[flag] === true) { // 3.0 boolean form → the 3.1 number form
      out[flag] = out[bound] ?? null
      delete out[bound]
    }
    if (out[flag] === false) delete out[flag]
  }
  if (typeof out.format === "string" && NUMBER_FORMATS.has(out.format)) delete out.format
  if (out.minimum === -SAFE_INTEGER) delete out.minimum
  if (out.maximum === SAFE_INTEGER) delete out.maximum
  if (out.nullable === false) delete out.nullable
}

/** The parts of a schema the contract fixes, in one form whichever generator wrote it. */
function norm(doc: OpenApiDocument, raw: unknown, base: string | undefined, depth = 0): JsonObject {
  const [node, at] = doc.resolve(raw, base)
  if (!isObject(node) || depth > 25) return {}
  const cx: Context = { doc, at, depth }
  const out: JsonObject = {}
  const props: JsonObject = {}
  const required = new Set<string>()
  mergeAllOf(node, cx, out, props, required)
  foldNullable(node, cx, out)
  for (const key of COMPARED_KEYS) if (node[key] !== undefined) out[key] = node[key]
  if (node.const !== undefined) out.enum = [node.const]
  tidy(out)
  for (const [name, prop] of Object.entries(asObject(node.properties))) props[name] = norm(doc, prop, at, depth + 1)
  for (const name of asArray(node.required)) if (typeof name === "string") required.add(name)
  if (Object.keys(props).length > 0) out.properties = props
  if (required.size > 0) out.required = [...required].sort()
  if (node.items !== undefined) out.items = norm(doc, node.items, at, depth + 1)
  return out
}

function diff(where: string, contract: unknown, served: unknown, found: string[]): void {
  if (isObject(contract) && isObject(served)) {
    const keys = new Set([...Object.keys(contract), ...Object.keys(served)])
    if ("format" in served && "pattern" in served && !("pattern" in contract)) keys.delete("pattern")
    for (const key of [...keys].sort()) diff(`${where}.${key}`, contract[key], served[key], found)
  } else if (JSON.stringify(contract) !== JSON.stringify(served)) {
    found.push(`${where}: contract ${JSON.stringify(contract)}, app ${JSON.stringify(served)}`)
  }
}

/** `GET /bookings/{}` — path parameter names differ between the contract and the code (`:id` or `{id}`). */
const routeKey = (method: string, p: string): string =>
  `${method.toUpperCase()} ${p.replace(/\{[^}]*\}|:[A-Za-z0-9_]+/g, "{}")}`

type Operation = { doc: OpenApiDocument; path: string; op: JsonObject; base: string | undefined }

function operations(doc: OpenApiDocument, prefix = ""): Map<string, Operation> {
  const found = new Map<string, Operation>()
  for (const [p, rawItem] of Object.entries(asObject(doc.root.paths))) {
    const [item, base] = doc.resolve(rawItem, doc.file)
    const served = prefix !== "" && p.startsWith(prefix) ? p.slice(prefix.length) : p
    for (const method of METHODS) {
      const op = asObject(item)[method]
      if (isObject(op)) found.set(routeKey(method, served), { doc, path: served, op, base })
    }
  }
  return found
}

function parameters({ doc, op, base }: Operation): JsonObject {
  const out: JsonObject = {}
  let position = 0
  for (const raw of asArray(op.parameters)) {
    const [resolved, at] = doc.resolve(raw, base)
    const param = asObject(resolved)
    const where = String(param.in)
    const name = String(param.name)
    if (where === "cookie" || (where === "header" && SKIPPED_HEADERS.has(name.toLowerCase()))) continue
    const schema = norm(doc, param.schema, at)
    delete schema.nullable // a query string has no null: an optional parameter is just not required
    out[where === "path" ? `path#${position++}` : `${where}:${name}`] = { required: param.required === true, schema }
  }
  return out
}

function bodies({ doc, base }: Operation, holder: unknown): JsonObject {
  const [resolved, at] = doc.resolve(holder, base)
  const out: JsonObject = {}
  for (const [media, spec] of Object.entries(asObject(asObject(resolved).content))) {
    out[media] = norm(doc, asObject(spec).schema, at)
  }
  return out
}

const statuses = (o: Operation): string[] =>
  Object.keys(asObject(o.op.responses)).filter((k) => !IGNORED_STATUSES.has(k)).sort()

function compare(key: string, c: Operation, s: Operation, found: string[]): void {
  if (c.op.operationId !== s.op.operationId) {
    found.push(`${key}: operationId contract ${JSON.stringify(c.op.operationId)}, app ${JSON.stringify(s.op.operationId)}`)
  }
  const name = `${key} (${String(c.op.operationId)})`
  diff(`${name} parameters`, parameters(c), parameters(s), found)
  diff(`${name} request body`, bodies(c, c.op.requestBody), bodies(s, s.op.requestBody), found)
  const [cCodes, sCodes] = [statuses(c), statuses(s)]
  if (JSON.stringify(cCodes) !== JSON.stringify(sCodes)) {
    found.push(`${name}: statuses contract ${JSON.stringify(cCodes)}, app ${JSON.stringify(sCodes)}`)
  }
  for (const code of cCodes.filter((x) => x.startsWith("2") && sCodes.includes(x))) {
    const response = (o: Operation): unknown => asObject(o.op.responses)[code]
    diff(`${name} response ${code}`, bodies(c, response(c)), bodies(s, response(s)), found)
  }
}

async function appDocument(): Promise<OpenApiDocument> {
  // The app registers @fastify/swagger in dynamic mode, with the type provider's schema transform. If it serves the
  // contract file itself (mode: "static"), app.swagger() returns that file and this test would compare the contract
  // with itself: give buildServer an option that registers dynamic mode here instead.
  const app = await buildServer(testDependencies())
  try {
    await app.ready()
    return new OpenApiDocument(asObject(app.swagger()))
  } finally {
    await app.close()
  }
}

describe("the app's OpenAPI against documentation/api/openapi.yaml", () => {
  it("serves every operation exactly as the contract describes it", async () => {
    const contract = OpenApiDocument.fromFile(CONTRACT)
    const served = await appDocument()
    const server = asObject(asArray(contract.root.servers)[0]).url
    const prefix = typeof server === "string" ? new URL(server, "http://contract.invalid").pathname.replace(/\/$/, "") : ""
    const expected = operations(contract)
    const actual = operations(served, prefix)
    const found: string[] = []
    for (const [key, s] of [...actual].sort(([a], [b]) => a.localeCompare(b))) {
      if (NOT_IN_CONTRACT.has(`${key.split(" ")[0] ?? ""} ${s.path}`)) continue
      const c = expected.get(key)
      if (c === undefined) found.push(`${key}: the app serves it, the contract has no such operation`)
      else compare(key, c, s, found)
    }
    const pending = [...expected.keys()].filter((k) => !actual.has(k)).sort()
    if (pending.length > 0) console.warn(`contract operations not served yet: ${pending.join(", ")}`)
    expect(found, "the app differs from documentation/api/openapi.yaml").toEqual([])
  })
})
