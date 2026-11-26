import { test } from "node:test";
import assert from "node:assert/strict";
import { existsSync, readFileSync } from "node:fs";

const router = readFileSync(new URL("../src/router/index.ts", import.meta.url), "utf8");
const exists = (p: string) => existsSync(new URL(`../src/${p}`, import.meta.url));

test("promotions, pages for buyers and their admin page are routed", () => {
  for (const path of ['path: "/promo"', 'path: "/info/:slug"', 'path: "pages"']) {
    assert.ok(router.includes(path), path);
  }
  for (const file of ["views/PromoPage.vue", "views/InfoPage.vue", "views/PagesManagement.vue"]) {
    assert.ok(exists(file), file);
  }
});

test("home page has the product tabs like shop.nag.uz", () => {
  const home = readFileSync(new URL("../src/views/HomePage.vue", import.meta.url), "utf8");
  for (const label of ["Рекомендуем", "Новинки", "Акции", "Популярное"]) {
    assert.ok(home.includes(label), label);
  }
});

test("footer lists the pages for buyers, header links to promotions", () => {
  const footer = readFileSync(
    new URL("../src/components/FooterComponent.vue", import.meta.url),
    "utf8",
  );
  assert.ok(footer.includes("Покупателям") && footer.includes("pagesAPI"));
  const header = readFileSync(
    new URL("../src/components/HeaderComponent.vue", import.meta.url),
    "utf8",
  );
  assert.ok(header.includes('to="/promo"'));
});
