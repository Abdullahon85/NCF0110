import { test } from "node:test";
import assert from "node:assert/strict";
import {
  activeChips,
  defaultState,
  parseCatalogQuery,
  rangeFromInputs,
  removeChip,
  SORT_LABELS,
  toApiParams,
  toRouteQuery,
  type CatalogFacets,
} from "../src/utils/catalogQuery.ts";

const full = {
  brand: "alpha,beta",
  status: "new",
  in_stock: "1",
  price_min: "100",
  price_max: "500",
  f12: "3,4",
  f15_min: "2",
  f15_max: "8",
  q: "камера",
  sort: "price",
  page: "3",
  per_page: "40",
  view: "list",
};

test("route query round trip", () => {
  assert.deepEqual(toRouteQuery(parseCatalogQuery(full)), full);
});

test("defaults are not written to the address", () => {
  assert.deepEqual(toRouteQuery(defaultState()), {});
  assert.deepEqual(toRouteQuery(parseCatalogQuery({})), {});
});

test("garbage in the address falls back to defaults", () => {
  const s = parseCatalogQuery({
    per_page: "7",
    page: "-1",
    f12: "a,3",
    price_min: "abc",
    sort: "x",
    view: "table",
    in_stock: "maybe",
    f9_min: "zz",
    tag: "x",
    ordering: "x",
  });
  assert.equal(s.perPage, 20);
  assert.equal(s.page, 1);
  assert.deepEqual(s.lists, { 12: [3] });
  assert.equal(s.priceMin, null);
  assert.equal(s.sort, "popular");
  assert.equal(s.view, "grid");
  assert.equal(s.inStock, false);
  assert.deepEqual(s.ranges, {});
});

test("array values from vue-router are accepted", () => {
  assert.deepEqual(parseCatalogQuery({ brand: ["alpha", null] }).brands, ["alpha"]);
});

test("api params use page_size and keep fixed params", () => {
  const p = toApiParams(parseCatalogQuery(full), { category: "kamery" });
  assert.equal(p.page_size, "40");
  assert.equal(p.f12, "3,4");
  assert.equal(p.category, "kamery");
  assert.equal(p.per_page, undefined);
  assert.equal(p.view, undefined);
  assert.equal(toApiParams(defaultState(), {}).page_size, "20");
});

const facets: CatalogFacets = {
  total: 2,
  price: { min: 10, max: 900 },
  in_stock: 1,
  categories: [],
  brands: [{ slug: "alpha", name: "Alpha", count: 1 }],
  statuses: [{ value: "new", label: "Новинка", count: 1 }],
  features: [
    {
      id: 12,
      name: "Цвет",
      group: "",
      type: "list",
      values: [{ ids: [3, 4], value: "Черный", count: 2 }],
    },
    { id: 15, name: "Разрешение", group: "", type: "range", unit: "Мп", min: 2, max: 8 },
  ],
};

test("chips name what is selected", () => {
  const labels = activeChips(parseCatalogQuery(full), facets).map((c) => c.label);
  assert.deepEqual(labels, [
    "Alpha",
    "beta",
    "Новинка",
    "В наличии",
    "Цена: от 100 до 500",
    "Цвет: Черный",
    "Разрешение: от 2 до 8 Мп",
    "Поиск: камера",
  ]);
});

test("removing one chip keeps the rest and resets the page", () => {
  const s = parseCatalogQuery(full);
  const chips = activeChips(s, facets);
  const color = chips.find((c) => c.label === "Цвет: Черный")!;
  const next = removeChip(s, color.key);
  assert.deepEqual(next.lists, {});
  assert.deepEqual(next.brands, ["alpha", "beta"]);
  assert.equal(next.page, 1);
  assert.deepEqual(removeChip(s, activeChips(s, facets)[0].key).brands, ["beta"]);
  assert.equal(removeChip(s, "price").priceMin, null);
});

test("sort labels", () => {
  assert.deepEqual(SORT_LABELS, {
    popular: "По популярности",
    price: "Сначала дешевле",
    "-price": "Сначала дороже",
    new: "Новинки",
    name: "По названию",
  });
});

test("range from inputs: the far ends of the slider mean no limit", () => {
  // prices 10.50 … 500.99, step 1: the right end of the slider is 500.5, still "no limit"
  assert.deepEqual(rangeFromInputs(null, 500.5, 10.5, 500.99, 1), { min: null, max: null });
  assert.deepEqual(rangeFromInputs(10.5, 500.99, 10.5, 500.99, 1), { min: null, max: null });
  assert.deepEqual(rangeFromInputs(100, 300, 10.5, 500.99, 1), { min: 100, max: 300 });
  // swapped and out-of-bounds values
  assert.deepEqual(rangeFromInputs(300, 100, 0, 1000, 5), { min: 100, max: 300 });
  assert.deepEqual(rangeFromInputs(-50, 5000, 0, 1000, 5), { min: null, max: null });
});
