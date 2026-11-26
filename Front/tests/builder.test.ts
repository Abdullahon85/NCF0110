import { test } from "node:test";
import assert from "node:assert/strict";
import {
  PIECES,
  SLOTS,
  place,
  removeAt,
  firstFreeSlot,
  summary,
  hints,
  requestText,
  type Placement,
} from "../src/components/builder/model.ts";

const slotFor = (piece: string) => SLOTS.find((s) => s.accepts.includes(piece as never))!.id;

test("eight pieces, each with a picture and a catalog search", () => {
  assert.deepEqual(
    PIECES.map((p) => p.id),
    ["dome", "bullet", "nvr", "poe", "router", "wifi", "access", "ups"],
  );
  for (const p of PIECES) {
    assert.equal(p.img, `/builder/${p.id}.webp`);
    assert.ok(p.label && p.search);
  }
});

test("every piece fits somewhere and slot positions are inside the scene", () => {
  for (const p of PIECES)
    assert.ok(
      SLOTS.some((s) => s.accepts.includes(p.id)),
      p.id,
    );
  for (const s of SLOTS) {
    assert.ok(s.x >= 0 && s.x <= 100 && s.y >= 0 && s.y <= 100, s.id);
  }
  assert.equal(new Set(SLOTS.map((s) => s.id)).size, SLOTS.length);
});

test("place is immutable and fills a free, matching slot", () => {
  const empty: Placement = {};
  const slot = slotFor("dome");
  const one = place(empty, slot, "dome");
  assert.deepEqual(empty, {});
  assert.equal(one[slot], "dome");
});

test("occupied, wrong-type and unknown slots are refused without changes", () => {
  const slot = slotFor("dome");
  const one = place({}, slot, "dome");
  assert.equal(place(one, slot, "bullet"), one);
  const nvrSlot = SLOTS.find((s) => !s.accepts.includes("dome"))!.id;
  assert.equal(place(one, nvrSlot, "dome"), one);
  assert.equal(place(one, "no-such-slot", "dome"), one);
});

test("removeAt frees a slot and leaves others", () => {
  const a = slotFor("nvr");
  const b = slotFor("ups");
  const p = place(place({}, a, "nvr"), b, "ups");
  const q = removeAt(p, a);
  assert.deepEqual(Object.keys(q), [b]);
  assert.equal(p[a], "nvr");
});

test("firstFreeSlot follows SLOTS order and returns null when all are taken", () => {
  let p: Placement = {};
  const domeSlots = SLOTS.filter((s) => s.accepts.includes("dome")).map((s) => s.id);
  assert.equal(firstFreeSlot(p, "dome"), domeSlots[0]);
  for (const id of domeSlots) p = place(p, id, firstFreeSlot(p, "dome") ? "dome" : "dome");
  // every slot that accepts a dome is now either a dome or blocked
  const free = SLOTS.filter((s) => s.accepts.includes("dome") && !p[s.id]);
  assert.equal(free.length, 0);
  assert.equal(firstFreeSlot(p, "dome"), null);
});

test("summary counts pieces in PIECES order and skips zeros", () => {
  let p: Placement = {};
  for (let i = 0; i < 2; i++) p = place(p, firstFreeSlot(p, "dome")!, "dome");
  p = place(p, firstFreeSlot(p, "ups")!, "ups");
  assert.deepEqual(
    summary(p).map((r) => [r.id, r.count]),
    [
      ["dome", 2],
      ["ups", 1],
    ],
  );
  assert.deepEqual(summary({}), []);
});

test("hints appear for cameras without recorder, without PoE, and equipment without UPS", () => {
  let p: Placement = place({}, firstFreeSlot({}, "dome")!, "dome");
  const h = hints(p).join(" | ");
  assert.match(h, /регистратор/);
  assert.match(h, /PoE/);
  assert.match(h, /ИБП/);
  p = place(p, firstFreeSlot(p, "nvr")!, "nvr");
  p = place(p, firstFreeSlot(p, "poe")!, "poe");
  p = place(p, firstFreeSlot(p, "ups")!, "ups");
  assert.deepEqual(hints(p), []);
  assert.deepEqual(hints({}), []);
});

test("requestText lists the system, and is empty for an empty scene", () => {
  assert.equal(requestText({}), "");
  let p: Placement = {};
  for (let i = 0; i < 3; i++) p = place(p, firstFreeSlot(p, "dome")!, "dome");
  p = place(p, firstFreeSlot(p, "nvr")!, "nvr");
  const text = requestText(p);
  assert.match(text, /^Здравствуйте! Хочу рассчитать систему:\n/);
  assert.match(text, /— Купольная камера × 3/);
  assert.match(text, /— Видеорегистратор × 1/);
});
