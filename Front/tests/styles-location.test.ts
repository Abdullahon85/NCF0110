// All CSS lives in src/styles/. A .vue file may only point at it:
//   <style scoped src="@/styles/views/HomePage.css"></style>
import { test } from "node:test";
import assert from "node:assert/strict";
import { readdirSync, readFileSync, statSync } from "node:fs";
import { join } from "node:path";

const SRC = new URL("../src/", import.meta.url).pathname;

function vueFiles(dir: string): string[] {
  return readdirSync(dir).flatMap((name) => {
    const path = join(dir, name);
    if (statSync(path).isDirectory()) return vueFiles(path);
    return name.endsWith(".vue") ? [path] : [];
  });
}

test("no .vue file contains inline CSS", () => {
  const offenders: string[] = [];
  for (const file of vueFiles(SRC)) {
    const text = readFileSync(file, "utf8");
    for (const m of text.matchAll(/<style\b([^>]*)>([\s\S]*?)<\/style>/g)) {
      const pointsToStyles = /\bsrc="@\/styles\/[^"]+\.css"/.test(m[1]);
      if (!pointsToStyles || m[2].trim() !== "") offenders.push(file.slice(SRC.length));
    }
  }
  assert.deepEqual(offenders, []);
});
