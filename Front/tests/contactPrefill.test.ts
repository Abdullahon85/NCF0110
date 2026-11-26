import { test } from "node:test";
import assert from "node:assert/strict";
import { contactPrefill } from "../src/utils/contactPrefill.ts";

test("takes the message from history state", () => {
  assert.equal(contactPrefill({ message: "Хочу рассчитать" }), "Хочу рассчитать");
});

test("caps the message at the backend limit of 3000 characters", () => {
  assert.equal(contactPrefill({ message: "x".repeat(5000) }).length, 3000);
});

test("ignores anything that is not a string message", () => {
  assert.equal(contactPrefill({ message: ["a"] }), "");
  assert.equal(contactPrefill(null), "");
  assert.equal(contactPrefill(undefined), "");
  assert.equal(contactPrefill("message"), "");
});
