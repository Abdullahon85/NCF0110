import { test } from "node:test";
import assert from "node:assert/strict";
import { itemWord, rejectedCartLines } from "../src/utils/cartOrder.ts";
import { readJson } from "../src/utils/storage.ts";

test("russian plural of товар", () => {
  const cases: [number, string][] = [
    [1, "товар"],
    [2, "товара"],
    [4, "товара"],
    [5, "товаров"],
    [11, "товаров"],
    [12, "товаров"],
    [14, "товаров"],
    [21, "товар"],
    [22, "товара"],
    [101, "товар"],
    [111, "товаров"],
    [112, "товаров"],
    [0, "товаров"],
  ];
  for (const [n, word] of cases) assert.equal(itemWord(n), word, String(n));
});

test("rejected cart lines are found from the 400 items list", () => {
  const err = {
    response: {
      status: 400,
      data: { items: [{}, { product: ["нет"] }, {}, { product: ["нет"] }] },
    },
  };
  assert.deepEqual(rejectedCartLines(err), [1, 3]);
});

test("other errors reject no cart line", () => {
  assert.deepEqual(
    rejectedCartLines({
      response: { status: 400, data: { items: ["Заказ должен содержать хотя бы один товар."] } },
    }),
    [],
  );
  assert.deepEqual(
    rejectedCartLines({ response: { status: 400, data: { customer_phone: ["x"] } } }),
    [],
  );
  assert.deepEqual(rejectedCartLines({ response: { status: 500 } }), []);
  assert.deepEqual(
    rejectedCartLines({ response: { status: 400, data: { items: [{ quantity: ["x"] }] } } }),
    [],
  );
  assert.deepEqual(rejectedCartLines(undefined), []);
});

test("broken localStorage entry falls back instead of throwing", () => {
  const store = (v: string | null) => ({ getItem: () => v });
  assert.deepEqual(readJson(store("[1,2]"), "k", []), [1, 2]);
  assert.deepEqual(readJson(store(null), "k", []), []);
  assert.deepEqual(readJson(store("{broken"), "k", []), []);
  assert.deepEqual(
    readJson(
      {
        getItem: () => {
          throw new Error("denied");
        },
      },
      "k",
      ["x"],
    ),
    ["x"],
  );
});
