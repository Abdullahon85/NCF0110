// The server accepts 1..999 of one product in an order (OrderItemSerializer).
export const MAX_QTY = 999;

export function clampQty(qty: number): number {
  return Number.isFinite(qty) ? Math.min(MAX_QTY, Math.max(1, Math.floor(qty))) : 1;
}
