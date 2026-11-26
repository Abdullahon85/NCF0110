// Dashboard data shaping: what needs the admin's attention, and the quiet totals.
// Uses only fields that /api/admin/stats/ returns today.

export interface DashboardStats {
  products_count?: number;
  available_products?: number;
  categories_count?: number;
  brands_count?: number;
  news_count?: number;
  orders_count?: number;
  new_orders_count?: number;
  total_messages?: number;
  unread_messages?: number;
}

export function ruPlural(n: number, forms: readonly [string, string, string]): string {
  const mod10 = n % 10;
  const mod100 = n % 100;
  if (mod10 === 1 && mod100 !== 11) return forms[0];
  if (mod10 >= 2 && mod10 <= 4 && (mod100 < 12 || mod100 > 14)) return forms[1];
  return forms[2];
}

export interface AttentionItem {
  key: "orders" | "messages";
  count: number;
  label: string;
  to: string;
}

export function attentionItems(stats: DashboardStats): AttentionItem[] {
  const items: AttentionItem[] = [];
  const orders = stats.new_orders_count ?? 0;
  const messages = stats.unread_messages ?? 0;
  if (orders > 0) {
    items.push({
      key: "orders",
      count: orders,
      label: ruPlural(orders, ["новый заказ", "новых заказа", "новых заказов"]),
      to: "/admin/orders",
    });
  }
  if (messages > 0) {
    items.push({
      key: "messages",
      count: messages,
      label: ruPlural(messages, [
        "непрочитанное сообщение",
        "непрочитанных сообщения",
        "непрочитанных сообщений",
      ]),
      to: "/admin/messages",
    });
  }
  return items;
}

export interface Figure {
  label: string;
  value: number;
  to: string;
}

export function quietFigures(stats: DashboardStats): Figure[] {
  const n = (v?: number) => v ?? 0;
  return [
    { label: "Товаров", value: n(stats.products_count), to: "/admin/products" },
    { label: "В наличии", value: n(stats.available_products), to: "/admin/products" },
    { label: "Каталогов", value: n(stats.categories_count), to: "/admin/categories" },
    { label: "Брендов", value: n(stats.brands_count), to: "/admin/brands" },
    { label: "Новостей", value: n(stats.news_count), to: "/admin/news" },
    { label: "Заказов всего", value: n(stats.orders_count), to: "/admin/orders" },
    { label: "Сообщений всего", value: n(stats.total_messages), to: "/admin/messages" },
  ];
}
