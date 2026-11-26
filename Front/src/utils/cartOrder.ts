// Helpers for the checkout on the cart page.

// Russian plural for "товар": 1 товар, 2 товара, 5 товаров, 11 товаров, 21 товар, 111 товаров.
export function itemWord(n: number): string {
  const m100 = Math.abs(n) % 100;
  const m10 = m100 % 10;
  if (m100 >= 11 && m100 <= 14) return "товаров";
  if (m10 === 1) return "товар";
  if (m10 >= 2 && m10 <= 4) return "товара";
  return "товаров";
}

// The cart lives in localStorage, so it can still hold a product that was deleted
// from the catalog. The server then rejects the whole order with
// 400 {"items": [{}, {"product": ["..."]}, ...]} (one entry per cart line, in order).
// Returns the indexes of the rejected lines; [] when the error is something else.
export function rejectedCartLines(error: any): number[] {
  if (error?.response?.status !== 400) return [];
  const items = error?.response?.data?.items;
  if (!Array.isArray(items)) return [];
  const bad: number[] = [];
  items.forEach((entry: unknown, idx: number) => {
    if (entry && typeof entry === "object" && "product" in (entry as object)) bad.push(idx);
  });
  return bad;
}
