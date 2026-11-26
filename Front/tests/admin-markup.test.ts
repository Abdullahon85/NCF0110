import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { basename } from "node:path";
import { vueFiles, isAdminFile } from "./vueClasses.ts";

// Admin pages rendered inside AdminLayout.
const pages = vueFiles()
  .filter(isAdminFile)
  .filter((p) => !/\/(AdminLogin|AdminLayout|AdminIcon)\.vue$/.test(p));

const template = (p: string) => readFileSync(p, "utf8").split(/<script\b/)[0];

test("there are admin pages to check", () => {
  assert.ok(pages.length >= 14, String(pages.length));
});

test("the page title lives only in the top bar", () => {
  for (const p of pages) assert.ok(!/<h1[\s>]/.test(template(p)), basename(p));
});

test("action glyphs are SVG icons, not emoji", () => {
  for (const p of pages) {
    const found = template(p).match(/➕|✏️|🗑️|👁️|🔍|✕|✅/g);
    assert.equal(found, null, `${basename(p)}: ${found?.join(" ")}`);
  }
});

test("icon-only buttons have an accessible name", () => {
  for (const p of pages) {
    for (const m of template(p).matchAll(
      /<button\b([^>]*)>\s*<AdminIcon\b[^>]*\/>\s*<\/button>/g,
    )) {
      assert.match(m[1], /(:)?aria-label=/, `${basename(p)}: <button${m[1]}>`);
    }
  }
});

test("pages that use AdminIcon import it", () => {
  for (const p of pages) {
    const text = readFileSync(p, "utf8");
    if (text.includes("<AdminIcon"))
      assert.match(
        text,
        /import AdminIcon from "@\/components\/admin\/AdminIcon\.vue"/,
        basename(p),
      );
  }
});

test("an empty list offers the page's create action", () => {
  for (const p of pages) {
    const t = template(p);
    if (!/@click="openCreateModal"/.test(t)) continue;
    const empty = t.match(/<td[^>]*class="empty"[^>]*>([\s\S]*?)<\/td>/);
    assert.ok(empty, `${basename(p)}: no empty cell`);
    assert.match(empty[1], /@click="openCreateModal"/, basename(p));
  }
});

test("headings start with words, not emoji", () => {
  const emoji = /\p{Extended_Pictographic}/u;
  for (const p of pages) {
    for (const m of template(p).matchAll(/<(h[2-4]|legend)\b[^>]*>([\s\S]*?)<\/\1>/g)) {
      assert.ok(!emoji.test(m[2]), `${basename(p)}: ${m[2].trim()}`);
    }
  }
});

test("login page: one title, icon toggle with a name, no emoji", () => {
  const p = vueFiles().find((f) => f.endsWith("/AdminLogin.vue"))!;
  const t = template(p);
  assert.equal((t.match(/<h1[\s>]/g) ?? []).length, 1);
  assert.equal(t.match(/\p{Extended_Pictographic}|←/gu), null);
  assert.match(t, /:aria-label="showPassword \? 'Скрыть пароль' : 'Показать пароль'"/);
  const legacy = readFileSync(new URL("../src/styles/admin/legacy.css", import.meta.url), "utf8");
  assert.ok(
    !/\.login-(page|container|header|form|btn|footer)\b/.test(legacy),
    "old login rules left in legacy.css",
  );
});
