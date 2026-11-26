import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync, readdirSync } from "node:fs";
import { SRC, adminOnlyClasses } from "./vueClasses.ts";

const escape = (s: string) => s.replace(/[-]/g, "\\-");

test("admin-only classes are not styled in the public stylesheets", () => {
  const leaks: string[] = [];
  const files = readdirSync(SRC + "styles/site")
    .filter((f) => f.endsWith(".css"))
    .map((f) => "styles/site/" + f);
  for (const file of files) {
    const css = readFileSync(SRC + file, "utf8").replace(/\/\*[\s\S]*?\*\//g, "");
    for (const cls of adminOnlyClasses()) {
      if (new RegExp(`\\.${escape(cls)}(?![\\w-])`).test(css)) leaks.push(`${file}: .${cls}`);
    }
  }
  assert.deepEqual(leaks, []);
});
