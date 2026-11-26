import { test } from "node:test";
import assert from "node:assert/strict";
import { ruPlural, attentionItems, quietFigures } from "../src/components/admin/dashboard.ts";

test("Russian plural forms", () => {
  const f = ["заказ", "заказа", "заказов"] as const;
  assert.deepEqual(
    [0, 1, 2, 4, 5, 11, 12, 14, 21, 22, 25, 101, 111].map((n) => ruPlural(n, f)),
    [
      "заказов",
      "заказ",
      "заказа",
      "заказа",
      "заказов",
      "заказов",
      "заказов",
      "заказов",
      "заказ",
      "заказа",
      "заказов",
      "заказ",
      "заказов",
    ],
  );
});

test("attention lists only what is waiting, orders first", () => {
  assert.deepEqual(attentionItems({ new_orders_count: 3, unread_messages: 1 }), [
    { key: "orders", count: 3, label: "новых заказа", to: "/admin/orders" },
    { key: "messages", count: 1, label: "непрочитанное сообщение", to: "/admin/messages" },
  ]);
  assert.deepEqual(
    attentionItems({ new_orders_count: 0, unread_messages: 5 }).map((i) => i.label),
    ["непрочитанных сообщений"],
  );
  assert.deepEqual(attentionItems({ new_orders_count: 0, unread_messages: 0 }), []);
  assert.deepEqual(attentionItems({}), []);
});

test("quiet figures keep their order and treat missing numbers as 0", () => {
  const rows = quietFigures({ products_count: 24, available_products: 20, categories_count: 12 });
  assert.deepEqual(
    rows.map((r) => [r.label, r.value]),
    [
      ["Товаров", 24],
      ["В наличии", 20],
      ["Каталогов", 12],
      ["Брендов", 0],
      ["Новостей", 0],
      ["Заказов всего", 0],
      ["Сообщений всего", 0],
    ],
  );
  assert.equal(rows[0].to, "/admin/products");
});
