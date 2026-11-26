// How a product's price and stock are shown on cards and on the product page.

type Num = number | string | null | undefined;

const toNumber = (v: Num): number | null => {
  if (v === null || v === undefined || v === "") return null;
  const n = Number(v);
  return Number.isFinite(n) ? n : null;
};

// 1500000 -> "1 500 000 сум" (non-breaking spaces between groups, as ru-RU formats them).
export function formatSum(value: Num): string {
  const n = toNumber(value) ?? 0;
  return `${new Intl.NumberFormat("ru-RU", { maximumFractionDigits: 0 }).format(n)} сум`;
}

export type StockLabel = { text: string; tone: "ok" | "order" };

// Not available, or 0 pieces -> "Под заказ" (can still be ordered); no number -> "В наличии";
// more than 10 -> "10+ шт".
export function stockLabel(p: {
  is_available: boolean;
  stock_quantity?: number | null;
}): StockLabel {
  const qty = p.stock_quantity ?? null;
  if (!p.is_available || qty === 0) return { text: "Под заказ", tone: "order" };
  if (qty === null) return { text: "В наличии", tone: "ok" };
  return { text: `В наличии: ${qty > 10 ? "10+" : qty} шт`, tone: "ok" };
}

// Text of the card's cart button: what is in stock is bought, the rest is ordered.
export function cartButtonText(p: {
  is_available: boolean;
  stock_quantity?: number | null;
}): string {
  return stockLabel(p).tone === "ok" ? "В корзину" : "Заказать";
}

export type PriceView = { price: string; old: string | null; discount: string | null };

// Old price and discount only when the server computed a discount (old_price > price > 0).
export function priceView(p: {
  price: Num;
  old_price?: Num;
  discount_percent?: number | null;
}): PriceView {
  const price = toNumber(p.price);
  if (price === null) return { price: "Цена по запросу", old: null, discount: null };
  const discount = p.discount_percent ?? null;
  return {
    price: formatSum(price),
    old: discount ? formatSum(p.old_price) : null,
    discount: discount ? `−${discount}%` : null,
  };
}

// Size of a document for the "Документация" tab: КБ below a megabyte, else МБ with one decimal.
export function fileSize(bytes: number | null | undefined): string {
  if (!bytes) return "";
  const mb = bytes / 1024 / 1024;
  return mb < 1 ? `${Math.max(1, Math.round(bytes / 1024))} КБ` : `${mb.toFixed(1)} МБ`;
}
