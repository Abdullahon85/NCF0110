import { test } from "node:test";
import assert from "node:assert/strict";
import { existsSync, readFileSync, readdirSync } from "node:fs";

const STYLES = new URL("../src/styles/", import.meta.url);
const SITE = new URL("site/", STYLES);
const read = (u: URL) => readFileSync(u, "utf8");

test("the two monolith stylesheets are gone", () => {
  assert.equal(existsSync(new URL("main.css", STYLES)), false);
  assert.equal(existsSync(new URL("mobile-improvements.css", STYLES)), false);
});

test("site/index.css imports only files that exist, each once", () => {
  const imports = [...read(new URL("index.css", SITE)).matchAll(/@import\s+"\.\/([^"]+)"/g)].map(
    (m) => m[1],
  );
  assert.ok(imports.length > 10, String(imports.length));
  assert.equal(new Set(imports).size, imports.length);
  for (const f of imports) assert.ok(existsSync(new URL(f, SITE)), f);
  const files = readdirSync(SITE).filter((f) => f.endsWith(".css") && f !== "index.css");
  assert.deepEqual(
    files.filter((f) => !imports.includes(f)),
    [],
    "files not imported",
  );
});

test("no site stylesheet is longer than 900 lines", () => {
  for (const f of readdirSync(SITE).filter((f) => f.endsWith(".css"))) {
    const n = read(new URL(f, SITE)).split("\n").length;
    assert.ok(n <= 900, `${f}: ${n}`);
  }
});

test("theme: site tokens live under .site and the app root gets that class outside the admin", () => {
  const theme = read(new URL("theme.css", SITE));
  for (const v of [
    "--site-paper: #f3f5f2",
    "--site-surface: #ffffff",
    "--site-line: #d7ddd8",
    "--site-ink: #111a15",
    "--site-muted: #4f5b54",
    "--site-deep: #0f2a1e",
    "--site-brand: #1b4332",
    "--site-signal: #f2b705",
    "--site-danger: #b42318",
    "--site-radius-card: 10px",
    "--site-radius-ctl: 8px",
    "--site-max: 1240px",
  ]) {
    assert.ok(theme.toLowerCase().includes(v), v);
  }
  assert.match(theme, /^\.site\s*\{/m);
  assert.doesNotMatch(theme, /:root/);
  assert.match(theme, /Onest Variable/);
  const app = readFileSync(new URL("../src/App.vue", import.meta.url), "utf8");
  assert.match(app, /:class="\{ site: !isAdminRoute \}"/);
  const main = readFileSync(new URL("../src/main.ts", import.meta.url), "utf8");
  assert.match(main, /@fontsource-variable\/onest/);
});
