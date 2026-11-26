import { test } from "node:test";
import assert from "node:assert/strict";
import { readdirSync, readFileSync } from "node:fs";

const src = new URL("../src/", import.meta.url);

test("the whole card opens the product: no separate «›» button", () => {
  const card = readFileSync(new URL("components/ProductCard.vue", src), "utf8");
  assert.ok(!card.includes("btn-view"));
  assert.match(card, /role="link"[\s\S]*tabindex="0"[\s\S]*@keydown\.enter="goToProduct"/);
  for (const f of readdirSync(new URL("styles/site/", src))) {
    const css = readFileSync(new URL(`styles/site/${f}`, src), "utf8");
    assert.ok(!css.includes(".btn-view"), f);
  }
});

test("card footer: labelled cart button and an accessible quantity stepper", () => {
  const card = readFileSync(new URL("components/ProductCard.vue", src), "utf8");
  assert.match(card, /class="btn-cart"[\s\S]*\{\{ cartText \}\}/);
  assert.match(card, /aria-label="Уменьшить количество"|:aria-label="cartQty <= 1/);
  assert.match(card, /aria-label="Увеличить количество"/);
  assert.match(card, /aria-live="polite"/);
  // the card buttons are styled in one place only
  for (const f of readdirSync(new URL("styles/site/", src)).filter(
    (n) => n !== "72-face-product-card.css",
  )) {
    const css = readFileSync(new URL(`styles/site/${f}`, src), "utf8");
    assert.ok(!/\.(btn-cart|card-qty-[a-z]+|product-footer-actions)\b/.test(css), f);
  }
});
