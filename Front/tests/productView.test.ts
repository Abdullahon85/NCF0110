import { test } from "node:test";
import assert from "node:assert/strict";
import {
  fileSize,
  formatSum,
  priceView,
  stockLabel,
  cartButtonText,
} from "../src/utils/productView.ts";

const NB = " ";

test("stock label like shop.nag.uz", () => {
  assert.deepEqual(stockLabel({ is_available: false, stock_quantity: 5 }), {
    text: "Под заказ",
    tone: "order",
  });
  assert.deepEqual(stockLabel({ is_available: true, stock_quantity: null }), {
    text: "В наличии",
    tone: "ok",
  });
  assert.deepEqual(stockLabel({ is_available: true, stock_quantity: 25 }), {
    text: "В наличии: 10+ шт",
    tone: "ok",
  });
  assert.deepEqual(stockLabel({ is_available: true, stock_quantity: 3 }), {
    text: "В наличии: 3 шт",
    tone: "ok",
  });
  assert.deepEqual(stockLabel({ is_available: true, stock_quantity: 0 }), {
    text: "Под заказ",
    tone: "order",
  });
});

test("sums in сум with spaces", () => {
  assert.equal(formatSum(1500000), `1${NB}500${NB}000 сум`);
  assert.equal(formatSum("82.00"), "82 сум");
});

test("price, old price and discount", () => {
  assert.deepEqual(priceView({ price: "82.00", old_price: "100.00", discount_percent: 18 }), {
    price: "82 сум",
    old: "100 сум",
    discount: "−18%",
  });
  assert.deepEqual(priceView({ price: "100.00", old_price: "90.00", discount_percent: null }), {
    price: "100 сум",
    old: null,
    discount: null,
  });
  assert.deepEqual(priceView({ price: null, old_price: "100.00", discount_percent: null }), {
    price: "Цена по запросу",
    old: null,
    discount: null,
  });
});

test("document size in КБ / МБ", () => {
  assert.equal(fileSize(700), "1 КБ");
  assert.equal(fileSize(250 * 1024), "250 КБ");
  assert.equal(fileSize(3.4 * 1024 * 1024), "3.4 МБ");
  assert.equal(fileSize(null), "");
});

test("cart button names the action: buy what is in stock, order the rest", () => {
  assert.equal(cartButtonText({ is_available: true, stock_quantity: 3 }), "В корзину");
  assert.equal(cartButtonText({ is_available: true, stock_quantity: null }), "В корзину");
  assert.equal(cartButtonText({ is_available: true, stock_quantity: 0 }), "Заказать");
  assert.equal(cartButtonText({ is_available: false, stock_quantity: 5 }), "Заказать");
});
