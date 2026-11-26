import { test } from "node:test";
import assert from "node:assert/strict";
import { existsSync, readFileSync } from "node:fs";

const read = (p: string) => readFileSync(new URL(`../src/${p}`, import.meta.url), "utf8");

test("one listing component with toolbar, facets, chips and pages", () => {
  const listing = read("components/catalog/ProductListing.vue");
  for (const part of [
    "<ListingToolbar",
    "<FacetPanel",
    "<ActiveChips",
    "<Pagination",
    "<ProductGrid",
  ]) {
    assert.ok(listing.includes(part), part);
  }
});

test("category, brand and search pages use the listing; filters are not kept in localStorage", () => {
  for (const page of [
    "views/CategoryProductsPage.vue",
    "views/Brand.vue",
    "views/CatalogPage.vue",
  ]) {
    const src = read(page);
    assert.ok(src.includes("<ProductListing"), page);
    assert.ok(!src.includes("localStorage") && !src.includes("catalog_filters_"), page);
  }
});

test("a filter fixed by the page is not offered again (brand page has no brand filter)", () => {
  assert.ok(read("components/catalog/ProductListing.vue").includes(':hide="Object.keys(fixed)"'));
  assert.ok(read("components/catalog/FacetPanel.vue").includes("hide.includes(g.key)"));
});

test("the listing reloads only when the page parameters really change", () => {
  // A parent re-render creates a new `fixed` object with the same content.
  assert.ok(read("components/catalog/ProductListing.vue").includes("JSON.stringify(props.fixed)"));
});

test("the old price slider component is gone", () => {
  assert.equal(existsSync(new URL("../src/components/PriceFilter.vue", import.meta.url)), false);
});
