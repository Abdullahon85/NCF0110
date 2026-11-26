import { test, mock } from "node:test";
import assert from "node:assert/strict";
import { readdirSync, readFileSync, statSync } from "node:fs";
import { join } from "node:path";
import { dismiss, toast, toasts, TOAST_MS } from "../src/components/admin/toast.ts";

test("toasts queue up and hide by themselves", () => {
  mock.timers.enable({ apis: ["setTimeout"] });
  try {
    toast.error("Ошибка удаления");
    toast.success("Сохранено");
    assert.deepEqual(
      toasts.value.map((t) => [t.text, t.tone]),
      [
        ["Ошибка удаления", "error"],
        ["Сохранено", "success"],
      ],
    );
    dismiss(toasts.value[0].id);
    assert.equal(toasts.value.length, 1);
    mock.timers.tick(TOAST_MS);
    assert.equal(toasts.value.length, 0);
  } finally {
    mock.timers.reset();
  }
});

test("no alert() left in the site and the admin panel", () => {
  const root = new URL("../src/", import.meta.url).pathname;
  const files: string[] = [];
  const walk = (dir: string) => {
    for (const name of readdirSync(dir)) {
      const p = join(dir, name);
      if (statSync(p).isDirectory()) walk(p);
      else if (/\.(vue|ts)$/.test(name)) files.push(p);
    }
  };
  walk(root);
  const offenders = files.filter((f) => /(^|[^.\w])alert\(/.test(readFileSync(f, "utf8")));
  assert.deepEqual(
    offenders.map((f) => f.slice(root.length)),
    [],
  );
});
