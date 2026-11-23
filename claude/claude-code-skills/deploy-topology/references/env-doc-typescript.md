# The env schema, generator and tests — TypeScript (zod)

The template of `env-and-config-contract.md` for a TypeScript backend: the schema module, config parsing from it, the
generator `backend/scripts/env-doc.ts`, the package scripts and the tests. Copy it and replace the example entries
(`MAIL_*` is a third-party mail API with a stub on the test stand) with the project's own; keep the shapes. Paths
follow `typescript-fastify`'s tree: `src/shared/providers/` — use the folder the architecture's §5 tree gives config.

## `src/shared/providers/env-schema.ts`

```ts
import { z } from "zod";

/** Blocks of the kit file and of DEPLOY.md's variables tables, in their order. */
export const ENV_BLOCKS = ["backend и migrate", "почта", "frontend"] as const;
export type EnvBlock = (typeof ENV_BLOCKS)[number];

/** The description of one variable: the kit file, DEPLOY.md and the root .env.example are rendered from it. */
export interface EnvDoc {
  readonly block: EnvBlock;
  readonly required: boolean;
  /** The «Обязательна» cell when the answer is conditional; «да» / «нет» otherwise. */
  readonly requiredNote?: string;
  readonly secret: boolean;
  /** Applied before parsing to an unset or empty variable; must pass the parser. */
  readonly default?: string;
  /** The kit file's value: real, or empty / <заглушка> for a secret and a per-site value. */
  readonly prod: string;
  /** «Для чего» — one line, above the variable in both files. */
  readonly purpose: string;
  readonly example: string;
  readonly details: string;
}

type Entry<T extends z.ZodType> = EnvDoc & { readonly parse: T };
const variable = <T extends z.ZodType>(parse: T, doc: EnvDoc): Entry<T> => ({ parse, ...doc });

const BACKEND = "backend и migrate";
const LOG_LEVELS = ["trace", "debug", "info", "warn", "error", "fatal"] as const;

export const ENV_SCHEMA = {
  APP_ENV: variable(z.enum(["test", "dev", "prod"]), {
    block: BACKEND, required: true, secret: false, prod: "prod",
    purpose: "среда приложения: test, dev или prod",
    example: "`prod`", details: "без неё процесс не стартует; заглушки разрешены только в test",
  }),
  LOG_LEVEL: variable(z.enum(LOG_LEVELS), {
    block: BACKEND, required: false, secret: false, default: "info", prod: "info",
    purpose: "подробность логов: trace, debug, info, warn, error, fatal",
    example: "`info`", details: "значение вне списка — процесс не стартует",
  }),
  SHUTDOWN_TIMEOUT_SEC: variable(z.coerce.number().int().min(1).max(25), {
    block: BACKEND, required: false, secret: false, default: "25", prod: "25",
    purpose: "сколько секунд дорабатывать запросы после SIGTERM",
    example: "`25`", details: "меньше 30 с grace period пода",
  }),
  DATABASE_URL: variable(z.string().url(), {
    block: BACKEND, required: true, secret: true,
    prod: "postgresql://<пользователь>:<пароль>@<хост>:5432/<база>?options=-csearch_path%3D<схема>",
    purpose: "подключение к PostgreSQL",
    example: "`postgresql://user:***@host:5432/db?options=-csearch_path%3D<схема>`",
    details: "у migrate — учётка-владелец схемы, у backend — учётка только для данных; у каждого контейнера своё значение",
  }),
  MAIL_API_URL: variable(z.string().url(), {
    block: "почта", required: true, secret: false, prod: "<адрес почтового сервиса>",
    purpose: "адрес почтового сервиса",
    example: "`https://mail.example.ru/api`", details: "на стенде test — заглушка mail-stub",
  }),
  MAIL_API_TOKEN: variable(z.string().min(1).optional(), {
    block: "почта", required: false, secret: true, prod: "",
    purpose: "токен почтового сервиса; пусто — письма не отправляются",
    example: "`***`", details: "Bearer-токен; без него процесс работает, писем нет",
  }),
} as const;

export type EnvKey = keyof typeof ENV_SCHEMA;
export const RECOGNIZED_ENV_KEYS = Object.keys(ENV_SCHEMA) as EnvKey[];
/** Required = `required` with no default; the start check and the tests use this one list. */
export const REQUIRED_ENV_KEYS = RECOGNIZED_ENV_KEYS.filter((key) => ENV_SCHEMA[key].required && ENV_SCHEMA[key].default === undefined);

/** The frontend image's variables (nginx): in the kit file and DEPLOY.md, never read by the backend. */
export const FRONTEND_ENV_VARIABLES: readonly (EnvDoc & { readonly name: string })[] = [
  {
    name: "BACKEND_SERVICE", block: "frontend", required: true, secret: false, prod: "<сервис backend>:3000",
    purpose: "куда nginx проксирует /api/", example: "`backend:3000`", details: "имя сервиса backend и его порт",
  },
  {
    name: "SECURE_MODE", block: "frontend", required: true, secret: false, prod: "plain",
    purpose: "plain — HTTP на 8080; secure — TLS на самом поде", example: "`plain`", details: "TLS обычно у ingress",
  },
];

/** Read only by compose (stand infrastructure), never by the app: root .env.example only. */
export const STAND_ENV_VARIABLES = [
  { name: "DEV_BIND", secret: false, purpose: "на каком интерфейсе открыт сайт стенда dev: 127.0.0.1 или 0.0.0.0" },
  { name: "DEV_DB_PASSWORD", secret: true, purpose: "пароль локальной PostgreSQL стенда dev" },
] as const;

/** What each .local file may hold — secrets and per-machine values — with the root .env.example's value. */
export const LOCAL_ENV_FILES: readonly { readonly file: string; readonly keys: readonly (readonly [string, string])[] }[] = [
  { file: ".env.test.local", keys: [["MAIL_API_TOKEN", ""]] },
  {
    file: ".env.dev.local",
    keys: [["MAIL_API_URL", ""], ["MAIL_API_TOKEN", ""], ["DEV_BIND", "127.0.0.1"], ["DEV_DB_PASSWORD", ""]],
  },
];
```

## `src/shared/providers/config.ts` — parsing from the schema

```ts
import { z } from "zod";

import { ENV_SCHEMA, RECOGNIZED_ENV_KEYS, type EnvKey } from "./env-schema.js";

export * from "./env-schema.js";

const envSchema = z.object(
  Object.fromEntries(RECOGNIZED_ENV_KEYS.map((key) => [key, ENV_SCHEMA[key].parse])) as {
    [K in EnvKey]: (typeof ENV_SCHEMA)[K]["parse"];
  },
);
export type AppEnv = z.infer<typeof envSchema>;

/** Only the schema's names; an empty value is unset, so the default goes in before parsing. Unknown names are ignored. */
function withDefaults(env: NodeJS.ProcessEnv): Record<EnvKey, string | undefined> {
  return Object.fromEntries(
    RECOGNIZED_ENV_KEYS.map((key) => {
      const value = env[key];
      return [key, value === undefined || value === "" ? ENV_SCHEMA[key].default : value];
    }),
  ) as Record<EnvKey, string | undefined>;
}

export function loadConfig(env: NodeJS.ProcessEnv = process.env): AppEnv {
  const parsed = envSchema.safeParse(withDefaults(env));
  // Names only: a value may be a secret.
  if (!parsed.success) throw new Error(`Invalid environment configuration: ${parsed.error.issues.map((issue) => issue.path.join(".")).join(", ")}`);
  // Then the fail-fast rules of env-and-config-contract.md: the mock gate, the paired flags, the placeholders.
  return parsed.data;
}
```

## `backend/scripts/env-doc.ts` — the generator

```ts
import { readFileSync, writeFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

import {
  ENV_BLOCKS, ENV_SCHEMA, FRONTEND_ENV_VARIABLES, LOCAL_ENV_FILES, RECOGNIZED_ENV_KEYS, REQUIRED_ENV_KEYS,
  STAND_ENV_VARIABLES, type EnvBlock, type EnvDoc,
} from "../src/shared/providers/env-schema.js";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../..");
const SCHEMA = "backend/src/shared/providers/env-schema.ts";
export const ENV_FILE = "deploy/prod.env.example";
export const DEPLOY_DOC = "documentation/deploy/deploy.md";
export const LOCAL_EXAMPLE = ".env.example";

type Documented = EnvDoc & { readonly name: string };

export function documentedVariables(): Documented[] {
  return [...RECOGNIZED_ENV_KEYS.map((name) => ({ name, ...ENV_SCHEMA[name] })), ...FRONTEND_ENV_VARIABLES];
}

const markers = (required: boolean, secret: boolean): string => `${required ? "[required] " : ""}${secret ? "[secret] " : ""}`;
const isRequired = (v: Documented): boolean => v.required && v.default === undefined;

export function renderEnvFile(variables = documentedVariables()): string {
  const blocks = ENV_BLOCKS.map((block) => {
    const pairs = variables.filter((v) => v.block === block).map((v) => `# ${markers(isRequired(v), v.secret)}${v.purpose}\n${v.name}=${v.prod}`);
    return [`# ===== ${block} =====`, ...pairs].join("\n\n");
  });
  return `${blocks.join("\n\n")}\n`;
}

function localDoc(name: string): { required: boolean; secret: boolean; purpose: string } {
  const stand = STAND_ENV_VARIABLES.find((v) => v.name === name);
  if (stand) return { required: false, secret: stand.secret, purpose: stand.purpose };
  if (name in ENV_SCHEMA) {
    const entry = ENV_SCHEMA[name as keyof typeof ENV_SCHEMA];
    return { required: (REQUIRED_ENV_KEYS as readonly string[]).includes(name), secret: entry.secret, purpose: entry.purpose };
  }
  throw new Error(`env-doc: ${name} of ${LOCAL_EXAMPLE} is neither in ENV_SCHEMA nor in STAND_ENV_VARIABLES`);
}

export function renderLocalExample(): string {
  const blocks = LOCAL_ENV_FILES.map(({ file, keys }) => {
    const pairs = keys.map(([name, value]) => {
      const doc = localDoc(name);
      return `# ${markers(doc.required, doc.secret)}${doc.purpose}\n${name}=${value}`;
    });
    return [`# ===== ${file} =====`, ...pairs].join("\n\n");
  });
  return `${blocks.join("\n\n")}\n`;
}

/** Which blocks each marker pair of deploy.md holds. */
export const DOC_TABLES: Record<string, readonly EnvBlock[]> = { backend: ["backend и migrate", "почта"], frontend: ["frontend"] };

export function renderTable(blocks: readonly EnvBlock[], variables = documentedVariables()): string {
  const rows = variables
    .filter((v) => blocks.includes(v.block))
    .map((v) => `| ${v.name} | ${v.requiredNote ?? (isRequired(v) ? "да" : "нет")} | ${v.secret ? "да" : "нет"} | ${v.example} | ${v.details} |`);
  return ["| Переменная | Обязательна | Секрет | Пример / формат | Что задаёт |", "|---|---|---|---|---|", ...rows].join("\n");
}

const open = (table: string): string => `<!-- env-doc:${table} — сгенерировано из ${SCHEMA} (npm run env:doc в backend/), руками не править -->`;
const close = (table: string): string => `<!-- /env-doc:${table} -->`;

export function renderDeployDoc(doc: string, variables = documentedVariables()): string {
  return Object.entries(DOC_TABLES).reduce((text, [table, blocks]) => {
    const pair = new RegExp(`<!-- env-doc:${table}[^>]*-->[\\s\\S]*?<!-- /env-doc:${table} -->`);
    if (!pair.test(text)) throw new Error(`env-doc: ${DEPLOY_DOC} has no <!-- env-doc:${table} … --> … <!-- /env-doc:${table} --> pair`);
    return text.replace(pair, () => `${open(table)}\n${renderTable(blocks, variables)}\n${close(table)}`);
  }, doc);
}

function rendered(root: string): Record<string, string> {
  return {
    [ENV_FILE]: renderEnvFile(),
    [DEPLOY_DOC]: renderDeployDoc(readFileSync(path.join(root, DEPLOY_DOC), "utf8")),
    [LOCAL_EXAMPLE]: renderLocalExample(),
  };
}

/** The generated files that differ from their render. */
export function staleFiles(root = ROOT): string[] {
  return Object.entries(rendered(root))
    .filter(([file, text]) => readFileSync(path.join(root, file), "utf8") !== text)
    .map(([file]) => file);
}

if (import.meta.url === pathToFileURL(process.argv[1] ?? "").href) {
  if (process.argv.includes("--check")) {
    const stale = staleFiles();
    for (const file of stale) process.stderr.write(`env-doc: ${file} differs from ${path.basename(SCHEMA)}; run npm run env:doc in backend/\n`);
    process.exit(stale.length === 0 ? 0 : 1);
  }
  for (const [file, text] of Object.entries(rendered(ROOT))) writeFileSync(path.join(ROOT, file), text);
}
```

`backend/package.json` scripts: `"env:doc": "tsx scripts/env-doc.ts"`, `"env:check": "tsx scripts/env-doc.ts --check"`.
eslint's `files`, knip's `entry` and `tsconfig.test.json`'s `include` name `scripts/**/*.ts`.

## `backend/tests/deploy/env-doc.test.ts`

```ts
import { spawnSync } from "node:child_process";
import { copyFileSync, existsSync, mkdirSync, mkdtempSync, readFileSync, rmSync, statSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { afterEach, describe, expect, it } from "vitest";
import { parse } from "yaml";

import { ENV_BLOCKS, ENV_SCHEMA, LOCAL_ENV_FILES, RECOGNIZED_ENV_KEYS, REQUIRED_ENV_KEYS, STAND_ENV_VARIABLES } from "../../src/shared/providers/config.js";
import { DEPLOY_DOC, ENV_FILE, LOCAL_EXAMPLE, documentedVariables, renderDeployDoc, renderEnvFile, renderLocalExample, staleFiles } from "../../scripts/env-doc.js";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../../..");
const read = (name: string): string => readFileSync(path.join(root, name), "utf8");
const dirs: string[] = [];
afterEach(() => { for (const dir of dirs.splice(0)) rmSync(dir, { recursive: true, force: true }); });
const tempDir = (prefix: string): string => { const dir = mkdtempSync(path.join(tmpdir(), prefix)); dirs.push(dir); return dir; };
const NAME_LINE = /^[A-Z][A-Z0-9_]*=/;

function expectLayout(text: string): void {
  expect(text).not.toMatch(/\n\n\n/);
  expect(text.endsWith("\n") && !text.endsWith("\n\n")).toBe(true);
  const lines = text.split("\n");
  lines.forEach((line, i) => {
    if (line.startsWith("# =====")) expect(lines[i + 1]).toBe("");
    if (!NAME_LINE.test(line)) return;
    expect(lines[i - 1]).toMatch(/^# (?:\[required\] )?(?:\[secret\] )?\S/);
    expect(lines[i - 2]).toBe("");
  });
}

describe("drift: the committed files are the render of the schema", () => {
  it("the kit file, deploy.md's tables and .env.example equal the render", () => {
    expect(staleFiles(root)).toEqual([]);
  });

  it("a hand edit of one file names that file alone", () => {
    const dir = tempDir("env-doc-");
    for (const file of [ENV_FILE, DEPLOY_DOC, LOCAL_EXAMPLE]) {
      mkdirSync(path.dirname(path.join(dir, file)), { recursive: true });
      copyFileSync(path.join(root, file), path.join(dir, file));
    }
    expect(staleFiles(dir)).toEqual([]);
    for (const file of [ENV_FILE, DEPLOY_DOC, LOCAL_EXAMPLE]) {
      // inside deploy.md only the tables are generated; the text around them is the author's
      writeFileSync(path.join(dir, file), file === DEPLOY_DOC ? read(file).replace("| Переменная |", "| Имя |") : `${read(file)}# hand edit\n`);
      expect(staleFiles(dir)).toEqual([file]);
      copyFileSync(path.join(root, file), path.join(dir, file));
    }
  });

  it("env:check exits 0 here; the package names both commands", () => {
    const run = spawnSync("npx", ["--no-install", "tsx", "scripts/env-doc.ts", "--check"], { cwd: path.join(root, "backend"), encoding: "utf8" });
    expect(run.status === 0 ? "" : run.stderr).toBe("");
    expect(JSON.parse(read("backend/package.json"))).toMatchObject({ scripts: { "env:doc": "tsx scripts/env-doc.ts", "env:check": "tsx scripts/env-doc.ts --check" } });
  });

  it("renderDeployDoc keeps the text around the markers and refuses a missing pair", () => {
    const doc = "до\n<!-- env-doc:backend старое -->\n| x |\n<!-- /env-doc:backend -->\nмежду\n<!-- env-doc:frontend -->\n<!-- /env-doc:frontend -->\nпосле\n";
    const out = renderDeployDoc(doc);
    expect(out.startsWith("до\n<!-- env-doc:backend ")).toBe(true);
    expect(out).toContain("<!-- /env-doc:backend -->\nмежду\n");
    expect(out.endsWith("<!-- /env-doc:frontend -->\nпосле\n")).toBe(true);
    expect(renderDeployDoc(out)).toBe(out);
    expect(() => renderDeployDoc("<!-- env-doc:backend -->\n<!-- /env-doc:backend -->\n")).toThrow(/env-doc:frontend/);
  });
});

describe("layout of both files", () => {
  it("the kit file: the schema's blocks in order, the marker line right above each NAME=value", () => {
    const text = renderEnvFile();
    expectLayout(text);
    expect(text.split("\n").filter((line) => line.startsWith("# ====="))).toEqual(ENV_BLOCKS.map((block) => `# ===== ${block} =====`));
    const names = text.split("\n").filter((line) => NAME_LINE.test(line)).map((line) => line.slice(0, line.indexOf("=")));
    expect(names).toEqual(documentedVariables().map((v) => v.name));
  });

  it(".env.example: headers are only the file names, values empty or a safe machine default, no placeholder", () => {
    const text = renderLocalExample();
    expectLayout(text);
    expect(text.split("\n").filter((line) => line.startsWith("# ====="))).toEqual(LOCAL_ENV_FILES.map(({ file }) => `# ===== ${file} =====`));
    expect(text).not.toMatch(/<[^>]+>/);
    expect(read(LOCAL_EXAMPLE)).toBe(text);
  });
});

describe("schema entries", () => {
  it("unique names, a one-line purpose, table cells filled and free of «|»", () => {
    const variables = documentedVariables();
    expect(new Set(variables.map((v) => v.name)).size).toBe(variables.length);
    for (const v of variables) {
      expect(v.purpose, v.name).toMatch(/^\S[^\n]*$/);
      expect(v.example, v.name).not.toBe("");
      expect(v.details, v.name).not.toBe("");
      expect(`${v.example}${v.details}`, v.name).not.toContain("|");
    }
  });

  it("each default passes its parser; a required entry's parser refuses an unset value", () => {
    for (const key of RECOGNIZED_ENV_KEYS) {
      const entry = ENV_SCHEMA[key];
      if (entry.default !== undefined) expect(entry.parse.safeParse(entry.default).success, `${key}=${entry.default}`).toBe(true);
      if ((REQUIRED_ENV_KEYS as readonly string[]).includes(key)) expect(entry.parse.safeParse(undefined).success, key).toBe(false);
    }
  });

  it("every .local key is in the schema or the compose-only list", () => {
    const known = new Set<string>([...RECOGNIZED_ENV_KEYS, ...STAND_ENV_VARIABLES.map((v) => v.name)]);
    for (const { keys } of LOCAL_ENV_FILES) for (const [name] of keys) expect(known.has(name), name).toBe(true);
  });
});

describe("compose contract", () => {
  const stands = { test: "docker-compose.test.yml", dev: "docker-compose.dev.yml" } as const;
  const environment = (file: string): Map<string, string> => {
    const compose = parse(read(file)) as { services: Record<string, { environment?: Record<string, string | number | boolean> }> };
    return new Map(Object.values(compose.services).flatMap((service) => Object.entries(service.environment ?? {}).map(([k, v]): [string, string] => [k, String(v)])));
  };

  it(".env.example lists exactly the keys the .local files may hold", () => {
    const keys = [...read(LOCAL_EXAMPLE).matchAll(/^([A-Z][A-Z0-9_]*)=/gm)].map((m) => m[1]);
    expect([...new Set(keys)].sort()).toEqual([...new Set(LOCAL_ENV_FILES.flatMap(({ keys: k }) => k.map(([name]) => name)))].sort());
  });

  it("no value a compose file fixes in environment: is repeated in that stand's .local file", () => {
    for (const [stand, file] of Object.entries(stands)) {
      const env = environment(file);
      const local = LOCAL_ENV_FILES.find(({ file: f }) => f === `.env.${stand}.local`)?.keys.map(([name]) => name) ?? [];
      for (const name of local) {
        const value = env.get(name);
        if (value !== undefined) expect(value, `${file}: ${name} is fixed in environment: and listed for .env.${stand}.local`).toContain(`\${${name}`);
      }
    }
  });

  it("each secret of the kit file is empty or a <placeholder>", () => {
    const kit = read(ENV_FILE);
    for (const v of documentedVariables().filter((d) => d.secret)) {
      const value = kit.match(new RegExp(`^${v.name}=(.*)$`, "m"))?.[1];
      expect(value, v.name).toBeDefined();
      if (value !== "") expect(value, v.name).toMatch(/<[^>]+>/);
    }
  });

  it("two stands and no prod in the repository", () => {
    expect(existsSync(path.join(root, "docker-compose.prod.yml"))).toBe(false);
    expect(read("Makefile")).not.toMatch(/^(up-prod|env-test|env-dev|env-prod|env):/m);
    for (const file of ["Makefile", ...Object.values(stands), LOCAL_EXAMPLE, "scripts/build-images.sh"]) {
      expect(read(file), file).not.toMatch(/\.env\.prod(\.migrate)?\.local|docker-compose\.prod|env_files\.py/);
    }
    for (const file of Object.values(stands)) expect(read(file), file).not.toMatch(/(?:path:\s*|env_file:\s*)\.env\.example/);
  });
});

/** A copy of the packaging inputs with docker and npm stubbed; npm's exit code is the test's choice. */
function packaging(npmExit: number): { dir: string; status: number | null; out: string } {
  const dir = tempDir("build-images-");
  for (const file of ["Makefile", "scripts/build-images.sh", ENV_FILE]) {
    mkdirSync(path.dirname(path.join(dir, file)), { recursive: true });
    copyFileSync(path.join(root, file), path.join(dir, file));
  }
  mkdirSync(path.join(dir, "bin"));
  writeFileSync(path.join(dir, "bin/docker"), '#!/bin/sh\necho "$*" >> "$CALLS"\n', { mode: 0o755 });
  writeFileSync(path.join(dir, "bin/npm"), '#!/bin/sh\n[ "$NPM_EXIT" = 0 ] || echo "env-doc: deploy/prod.env.example differs" >&2\nexit "$NPM_EXIT"\n', { mode: 0o755 });
  const run = spawnSync("make", ["build-images"], {
    cwd: dir, encoding: "utf8",
    env: { ...process.env, NPM_EXIT: String(npmExit), CALLS: path.join(dir, "docker-calls"), PATH: `${path.join(dir, "bin")}${path.delimiter}${process.env.PATH ?? ""}` },
  });
  return { dir, status: run.status, out: run.stdout + run.stderr };
}

describe("make", () => {
  it("build-images with a failing env:check stops before Docker and writes no release/", () => {
    const { dir, status, out } = packaging(1);
    expect(status).not.toBe(0);
    expect(out).toContain(ENV_FILE);
    expect(existsSync(path.join(dir, "docker-calls"))).toBe(false);
    expect(existsSync(path.join(dir, "release"))).toBe(false);
  });

  it("build-images.sh runs env:check before any docker call and before the kit copy", () => {
    const script = read("scripts/build-images.sh");
    const check = script.indexOf("run --silent env:check");
    expect(check).toBeGreaterThan(0);
    expect(check).toBeLessThan(script.indexOf("docker "));
    expect(check).toBeLessThan(script.indexOf(`cp ${ENV_FILE}`));
  });

  it(".env.test.local: created empty with mode 0600, an existing one kept", () => {
    const dir = tempDir("stand-");
    copyFileSync(path.join(root, "Makefile"), path.join(dir, "Makefile"));
    expect(spawnSync("make", [".env.test.local"], { cwd: dir }).status).toBe(0);
    const file = path.join(dir, ".env.test.local");
    expect(readFileSync(file, "utf8")).toBe("");
    expect(statSync(file).mode & 0o777).toBe(0o600);
    writeFileSync(file, "MAIL_API_TOKEN=synthetic\n");
    expect(spawnSync("make", [".env.test.local"], { cwd: dir }).status).toBe(0);
    expect(readFileSync(file, "utf8")).toBe("MAIL_API_TOKEN=synthetic\n");
  });

  it("up-dev without .env.dev.local stops before Docker and names the file", () => {
    const dir = tempDir("stand-");
    copyFileSync(path.join(root, "Makefile"), path.join(dir, "Makefile"));
    const run = spawnSync("make", ["up-dev"], { cwd: dir, encoding: "utf8", env: { ...process.env, PATH: `/nonexistent${path.delimiter}${process.env.PATH ?? ""}` } });
    expect(run.status).not.toBe(0);
    expect(run.stderr).toContain(".env.dev.local");
    expect(existsSync(path.join(dir, ".env.dev.local"))).toBe(false);
  });
});
```

`yaml` is a dev dependency (or the project's own compose reader, if it has one). The old `env-files.test.ts`, when
the project has one, is deleted in the same commit.

## `scripts/build-images.sh` and the Makefile — the lines that matter

```sh
set -eu
root=$(cd "$(dirname "$0")/.." && pwd)
cd "$root"
# deploy/prod.env.example and deploy.md's variables tables are rendered from the schema; a stale one stops the build
# before Docker (needs `npm ci` in backend/).
npm --prefix backend run --silent env:check
# … the images, the tar …
cp deploy/prod.env.example "$out_dir/${project}.env.example"
```

The Makefile's stand targets are `compose-shape.md` → Make/task-runner targets.
