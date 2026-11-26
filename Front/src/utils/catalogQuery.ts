// Filters, sorting and page of a product list, kept in the page address (shareable link,
// the Back button restores them). Same parameter names as the API (back/api/catalog.py),
// plus per_page and view, which only the page uses.

export type Sort = "popular" | "price" | "-price" | "new" | "name";
export type PerPage = 20 | 40 | 80;
export type Range = { min: number | null; max: number | null };

export type CatalogState = {
  brands: string[];
  statuses: string[];
  inStock: boolean;
  priceMin: number | null;
  priceMax: number | null;
  lists: Record<number, number[]>; // facet id -> selected value ids
  ranges: Record<number, Range>; // facet id -> numeric range
  q: string;
  sort: Sort;
  page: number;
  perPage: PerPage;
  view: "grid" | "list";
};

export type FacetValue = { ids: number[]; value: string; count: number };
export type FeatureFacet =
  | { id: number; name: string; group: string; type: "list" | "bool"; values: FacetValue[] }
  | {
      id: number;
      name: string;
      group: string;
      type: "range";
      unit: string;
      min: number;
      max: number;
    };

export type CatalogFacets = {
  total: number;
  price: { min: number | null; max: number | null };
  in_stock: number;
  categories: { slug: string; name: string; count: number }[];
  brands: { slug: string; name: string; count: number }[];
  statuses: { value: string; label: string; count: number }[];
  features: FeatureFacet[];
};

export const SORT_LABELS: Record<Sort, string> = {
  popular: "По популярности",
  price: "Сначала дешевле",
  "-price": "Сначала дороже",
  new: "Новинки",
  name: "По названию",
};
export const PER_PAGE: PerPage[] = [20, 40, 80];

export const defaultState = (): CatalogState => ({
  brands: [],
  statuses: [],
  inStock: false,
  priceMin: null,
  priceMax: null,
  lists: {},
  ranges: {},
  q: "",
  sort: "popular",
  page: 1,
  perPage: 20,
  view: "grid",
});

type QueryValue = string | null | undefined | (string | null)[];

const first = (v: QueryValue): string => (Array.isArray(v) ? (v.find((x) => x) ?? "") : (v ?? ""));
const csv = (v: QueryValue): string[] =>
  first(v)
    .split(",")
    .map((s) => s.trim())
    .filter(Boolean);
const num = (v: QueryValue): number | null => {
  const s = first(v).trim();
  if (!s) return null;
  const n = Number(s.replace(",", "."));
  return Number.isFinite(n) ? n : null;
};

export function parseCatalogQuery(query: Record<string, QueryValue>): CatalogState {
  const s = defaultState();
  s.brands = csv(query.brand);
  s.statuses = csv(query.status);
  s.inStock = first(query.in_stock) === "1";
  s.priceMin = num(query.price_min);
  s.priceMax = num(query.price_max);
  s.q = first(query.q).trim();
  const sort = first(query.sort);
  if (sort in SORT_LABELS) s.sort = sort as Sort;
  const page = Number(first(query.page));
  if (Number.isInteger(page) && page > 1) s.page = page;
  const perPage = Number(first(query.per_page));
  if ((PER_PAGE as number[]).includes(perPage)) s.perPage = perPage as PerPage;
  if (first(query.view) === "list") s.view = "list";
  for (const [key, value] of Object.entries(query)) {
    const list = /^f(\d+)$/.exec(key);
    if (list) {
      const ids = csv(value)
        .filter((x) => /^\d+$/.test(x))
        .map(Number);
      if (ids.length) s.lists[Number(list[1])] = ids;
      continue;
    }
    const range = /^f(\d+)_(min|max)$/.exec(key);
    const n = range ? num(value) : null;
    if (range && n !== null) {
      const r = (s.ranges[Number(range[1])] ??= { min: null, max: null });
      r[range[2] as "min" | "max"] = n;
    }
  }
  return s;
}

// Filters only (what both the list and the facets requests need).
function filterParams(s: CatalogState): Record<string, string> {
  const out: Record<string, string> = {};
  if (s.brands.length) out.brand = s.brands.join(",");
  if (s.statuses.length) out.status = s.statuses.join(",");
  if (s.inStock) out.in_stock = "1";
  if (s.priceMin !== null) out.price_min = String(s.priceMin);
  if (s.priceMax !== null) out.price_max = String(s.priceMax);
  for (const [id, ids] of Object.entries(s.lists)) if (ids.length) out[`f${id}`] = ids.join(",");
  for (const [id, r] of Object.entries(s.ranges)) {
    if (r.min !== null) out[`f${id}_min`] = String(r.min);
    if (r.max !== null) out[`f${id}_max`] = String(r.max);
  }
  if (s.q) out.q = s.q;
  return out;
}

export function toRouteQuery(s: CatalogState): Record<string, string> {
  const out = filterParams(s);
  if (s.sort !== "popular") out.sort = s.sort;
  if (s.page > 1) out.page = String(s.page);
  if (s.perPage !== 20) out.per_page = String(s.perPage);
  if (s.view !== "grid") out.view = s.view;
  return out;
}

export function toApiParams(
  s: CatalogState,
  fixed: Record<string, string>,
): Record<string, string> {
  return {
    ...filterParams(s),
    ...fixed,
    sort: s.sort,
    page: String(s.page),
    page_size: String(s.perPage),
  };
}

export type Chip = { key: string; label: string };

const rangeText = (r: Range, unit = "") =>
  [r.min !== null ? `от ${r.min}` : "", r.max !== null ? `до ${r.max}` : "", unit]
    .filter(Boolean)
    .join(" ");

export function activeChips(s: CatalogState, facets: CatalogFacets | null): Chip[] {
  const chips: Chip[] = [];
  for (const slug of s.brands) {
    chips.push({
      key: `brand:${slug}`,
      label: facets?.brands.find((b) => b.slug === slug)?.name ?? slug,
    });
  }
  for (const value of s.statuses) {
    chips.push({
      key: `status:${value}`,
      label: facets?.statuses.find((x) => x.value === value)?.label ?? value,
    });
  }
  if (s.inStock) chips.push({ key: "in_stock", label: "В наличии" });
  if (s.priceMin !== null || s.priceMax !== null) {
    chips.push({ key: "price", label: `Цена: ${rangeText({ min: s.priceMin, max: s.priceMax })}` });
  }
  for (const [id, ids] of Object.entries(s.lists)) {
    const facet = facets?.features.find((f) => f.id === Number(id));
    if (facet && facet.type !== "range") {
      for (const v of facet.values.filter((v) => v.ids.some((x) => ids.includes(x)))) {
        chips.push({ key: `f${id}:${v.ids.join("-")}`, label: `${facet.name}: ${v.value}` });
      }
    } else {
      chips.push({ key: `f${id}:${ids.join("-")}`, label: "Характеристика" });
    }
  }
  for (const [id, r] of Object.entries(s.ranges)) {
    const facet = facets?.features.find((f) => f.id === Number(id));
    const unit = facet?.type === "range" ? facet.unit : "";
    chips.push({
      key: `r${id}`,
      label: `${facet?.name ?? "Характеристика"}: ${rangeText(r, unit)}`,
    });
  }
  if (s.q) chips.push({ key: "q", label: `Поиск: ${s.q}` });
  return chips;
}

export function removeChip(s: CatalogState, key: string): CatalogState {
  const next: CatalogState = structuredClone(s);
  next.page = 1;
  const [kind, rest = ""] = key.split(":");
  if (kind === "brand") next.brands = next.brands.filter((b) => b !== rest);
  else if (kind === "status") next.statuses = next.statuses.filter((x) => x !== rest);
  else if (kind === "in_stock") next.inStock = false;
  else if (kind === "price") next.priceMin = next.priceMax = null;
  else if (kind === "q") next.q = "";
  else if (/^f\d+$/.test(kind)) {
    const id = Number(kind.slice(1));
    const drop = rest.split("-").map(Number);
    const left = (next.lists[id] ?? []).filter((x) => !drop.includes(x));
    if (left.length) next.lists[id] = left;
    else delete next.lists[id];
  } else if (/^r\d+$/.test(kind)) delete next.ranges[Number(kind.slice(1))];
  return next;
}

// Range typed or dragged by the visitor -> filter value. Out-of-bounds values are clamped,
// swapped ends are put in order, and an end within one slider step of the edge means
// "no limit" (the slider starts at `min` in steps, so its right end may stop just short
// of `max`: 500.5 for prices up to 500.99 — the dearest products must not vanish).
export function rangeFromInputs(
  low: number | null,
  high: number | null,
  min: number,
  max: number,
  step: number,
): Range {
  const clamp = (v: number | null) =>
    v === null || !Number.isFinite(v) ? null : Math.min(max, Math.max(min, v));
  let a = clamp(low);
  let b = clamp(high);
  if (a !== null && b !== null && a > b) [a, b] = [b, a];
  return {
    min: a === null || a < min + step ? null : a,
    max: b === null || b > max - step ? null : b,
  };
}
