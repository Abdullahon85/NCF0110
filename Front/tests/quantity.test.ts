import { test } from "node:test";
import assert from "node:assert/strict";
import { clampQty, MAX_QTY } from "../src/utils/quantity.ts";

test("quantity stays within 1..999 (server limit)", () => {
  assert.equal(MAX_QTY, 999);
  assert.equal(clampQty(5), 5);
  assert.equal(clampQty(0), 1);
  assert.equal(clampQty(-3), 1);
  assert.equal(clampQty(1500), 999);
  assert.equal(clampQty(2.7), 2);
  assert.equal(clampQty(NaN), 1);
});
