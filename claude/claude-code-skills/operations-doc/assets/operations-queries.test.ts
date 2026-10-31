import { readFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import postgres from "postgres";
import { afterAll, describe, expect, it } from "vitest";

/**
 * Reference test of operations-doc → references/proof.md → The query test, for a TypeScript backend on PostgreSQL
 * (vitest + the `postgres` driver). Copy it into the project's integration tests (beside deploy-topology's sync test)
 * and adapt the lines marked ADAPT; nothing else should need a change.
 *
 * Without a database: every ```sql block of documentation/operations/operations.md stands under a «**З-n.**» or
 * «**П-n.**» heading, ids are numbered in order and every id the text names is defined, a З- block is one read-only
 * statement (SELECT or WITH), every table is schema-qualified, and the document cites no requirement, actor or frame
 * id. With TEST_DATABASE_URL: each З- query is PREPAREd inside a READ ONLY transaction (tables, columns, types and $n
 * are checked; nothing runs); each П- procedure runs inside a transaction that is always rolled back (CREATE ROLE
 * included), a psql variable (:'name') replaced by a literal. A failure names the id and the database error, so a
 * migration that renames a column fails the build that renames it, not the operator at night.
 */

// ADAPT: the path from this file to the repository root.
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../..");
const DOC = "documentation/operations/operations.md";
// ADAPT: the schema the document's queries name (`<schema>.<table>`).
const SCHEMA = "app";
// ADAPT: how the project's integration tests get their database (often a helper such as readIntegrationEnv()).
const DATABASE_URL = process.env.TEST_DATABASE_URL;

interface SqlBlock {
  id: string;
  sql: string;
}

/** ```sql blocks with the id of the nearest «**З-n.**» / «**П-n.**» heading above each. */
function sqlBlocks(doc: string): SqlBlock[] {
  const blocks: SqlBlock[] = [];
  let id: string | null = null;
  let body: string[] | null = null;
  for (const line of doc.split("\n")) {
    if (body !== null) {
      if (line.startsWith("```")) {
        blocks.push({ id: id ?? "без заголовка", sql: body.join("\n").trim() });
        body = null;
      } else {
        body.push(line);
      }
      continue;
    }
    const heading = /^\*\*([ЗП]-\d+)\./.exec(line);
    if (heading) id = heading[1];
    if (line.trim() === "```sql") body = [];
  }
  return blocks;
}

/** Statements of a block, split on a `;` at a line end (the document's queries hold no `;` inside a string). */
function statements(sql: string): string[] {
  return sql
    .split(/;[ \t]*(?:\n|$)/)
    .map((s) => s.trim())
    .filter((s) => s.length > 0);
}

/** A psql variable is how the operator passes a secret; the test passes a literal. */
function withPsqlVariables(sql: string): string {
  return sql.replace(/:'\w+'/g, "'operations-doc-test'");
}

/** FROM / JOIN targets outside SCHEMA, CTE names and function calls aside. */
function unqualifiedTables(sql: string): string[] {
  const ctes = new Set([...sql.matchAll(/(?:\bWITH|,)\s+(\w+)\s+AS\s*\(/gi)].map((m) => m[1].toLowerCase()));
  return [...sql.matchAll(/\b(?:FROM|JOIN)\s+(?:LATERAL\s+)?([A-Za-z_]\w*)(\.[A-Za-z_]\w*)?(\s*\()?/gi)]
    .filter(([, first, , call]) => !call && first.toUpperCase() !== "LATERAL")
    .filter(([, first, rest]) => (rest === undefined ? !ctes.has(first.toLowerCase()) : first !== SCHEMA))
    .map(([match]) => match.trim());
}

const doc = readFileSync(path.join(root, DOC), "utf8");
const blocks = sqlBlocks(doc);
const queries = blocks.filter((b) => b.id.startsWith("З-"));
const procedures = blocks.filter((b) => b.id.startsWith("П-"));

describe(`${DOC}: shape`, () => {
  it("has queries, every sql block under a З-/П- heading", () => {
    expect(queries.length).toBeGreaterThan(0);
    expect(blocks.filter((b) => !/^[ЗП]-/.test(b.id)).map((b) => b.sql.slice(0, 60))).toEqual([]);
  });

  it("numbers ids in document order, and every id the text names is defined", () => {
    const defined = [...doc.matchAll(/^\*\*([ЗП]-\d+)\./gm)].map((m) => m[1]);
    for (const prefix of ["З-", "П-"]) {
      const ids = defined.filter((id) => id.startsWith(prefix));
      expect(ids, `${prefix} ids in document order`).toEqual(ids.map((_, i) => `${prefix}${i + 1}`));
    }
    const named = new Set([...doc.matchAll(/(?<![\p{L}\d-])([ЗП]-\d+)(?!\d)/gu)].map((m) => m[1]));
    expect([...named].filter((id) => !defined.includes(id)), "ids named but not defined").toEqual([]);
  });

  it("names no requirement, actor or frame id", () => {
    expect(doc.match(/\b(?:FR|NFR|BR|UC)-\d+|\b[AS]-\d+\b/g) ?? []).toEqual([]);
  });

  it.each(queries.map((q) => [q.id, q] as const))("%s is one read-only statement", (_id, q) => {
    expect(statements(q.sql), `${q.id}: one statement`).toHaveLength(1);
    expect(q.sql.replace(/--[^\n]*/g, "").trim(), `${q.id}: starts with SELECT or WITH`).toMatch(/^(SELECT|WITH)\b/i);
  });

  it.each(blocks.map((b) => [b.id, b] as const))("%s names every table with its schema", (_id, b) => {
    expect(unqualifiedTables(b.sql), `${b.id}: tables outside ${SCHEMA}`).toEqual([]);
  });
});

describe.skipIf(!DATABASE_URL)(`${DOC}: queries against the schema`, () => {
  const sql = postgres(DATABASE_URL ?? "", { max: 1, onnotice: () => {} });

  afterAll(async () => {
    await sql.end();
  });

  async function inRolledBackTransaction(readOnly: boolean, fn: (tx: postgres.ReservedSql) => Promise<void>): Promise<void> {
    const tx = await sql.reserve();
    try {
      await tx.unsafe(readOnly ? "BEGIN READ ONLY" : "BEGIN");
      await fn(tx);
    } finally {
      await tx.unsafe("ROLLBACK");
      tx.release();
    }
  }

  async function named(id: string, step: () => Promise<unknown>): Promise<void> {
    try {
      await step();
    } catch (error) {
      const code = error instanceof Error && "code" in error ? String(error.code) : "";
      const message = error instanceof Error ? error.message : String(error);
      throw new Error(`${id}: ${code} ${message}`, { cause: error });
    }
  }

  it.each(queries.map((q) => [q.id, q] as const))("%s prepares in a read-only transaction", async (id, q) => {
    await inRolledBackTransaction(true, async (tx) => {
      await named(id, () => tx.unsafe(`PREPARE operations_doc_query AS ${statements(q.sql)[0]}`));
      await tx.unsafe("DEALLOCATE operations_doc_query");
    });
  });

  it.each(procedures.map((p) => [p.id, p] as const))("%s runs and rolls back", async (id, p) => {
    await inRolledBackTransaction(false, async (tx) => {
      for (const [n, statement] of statements(withPsqlVariables(p.sql)).entries()) {
        await named(`${id}, statement ${n + 1}`, () => tx.unsafe(statement));
      }
    });
  });
});
