// Run: npm test   (node --test, no extra dependencies)
import { test } from "node:test";
import assert from "node:assert/strict";
import { makeSlug } from "../src/utils/slug.ts";

test("cyrillic name -> ascii slug", () => {
  assert.equal(makeSlug("Камеры"), "kamery");
  assert.equal(makeSlug("Камера X"), "kamera-x");
});

test("uzbek cyrillic letters", () => {
  assert.equal(makeSlug("Ўзбек қовун"), "ozbek-qovun");
  assert.equal(makeSlug("Ғишт Ҳовли"), "gisht-hovli");
});

test("uzbek latin apostrophes are dropped", () => {
  assert.equal(makeSlug("O‘zbekiston"), "ozbekiston");
  assert.equal(makeSlug("G'isht"), "gisht");
});

test("spaces, symbols and repeated dashes", () => {
  assert.equal(makeSlug("  IP  камера — 4K!  "), "ip-kamera-4k");
});

test("symbols only -> empty (server fills it)", () => {
  assert.equal(makeSlug("!!!"), "");
});
