import type { IconName } from "./icons";

export type BadgeKey = "orders" | "messages";

export interface MenuItem {
  path: string;
  label: string;
  icon: IconName;
  badge?: BadgeKey;
}

export interface MenuGroup {
  title: string | null;
  items: MenuItem[];
}

// Grouped by the kind of work: incoming requests first, then the catalog, then the site.
export const adminMenu: MenuGroup[] = [
  { title: null, items: [{ path: "/admin", label: "Обзор", icon: "dashboard" }] },
  {
    title: "Работа",
    items: [
      { path: "/admin/orders", label: "Заказы", icon: "orders", badge: "orders" },
      { path: "/admin/messages", label: "Сообщения", icon: "messages", badge: "messages" },
      { path: "/admin/reviews", label: "Отзывы", icon: "reviews" },
      { path: "/admin/questions", label: "Вопросы", icon: "questions" },
    ],
  },
  {
    title: "Каталог",
    items: [
      { path: "/admin/products", label: "Товары", icon: "products" },
      { path: "/admin/categories", label: "Каталоги", icon: "categories" },
      { path: "/admin/brands", label: "Бренды", icon: "brands" },
      { path: "/admin/features", label: "Характеристики", icon: "features" },
    ],
  },
  {
    title: "Сайт",
    items: [
      { path: "/admin/banners", label: "Баннеры", icon: "banners" },
      { path: "/admin/news", label: "Новости", icon: "news" },
      { path: "/admin/pages", label: "Страницы", icon: "pages" },
      { path: "/admin/settings", label: "Настройки", icon: "settings" },
    ],
  },
];

const TITLES: Record<string, string> = {
  "/admin": "Обзор",
  "/admin/orders": "Заказы",
  "/admin/messages": "Сообщения",
  "/admin/reviews": "Отзывы",
  "/admin/questions": "Вопросы",
  "/admin/products": "Товары",
  "/admin/categories": "Каталоги",
  "/admin/brands": "Бренды",
  "/admin/features": "Характеристики",
  "/admin/banners": "Баннеры",
  "/admin/news": "Новости",
  "/admin/pages": "Страницы для покупателей",
  "/admin/settings": "Настройки сайта",
  "/admin/profile": "Профиль",
};

export function pageTitle(path: string): string {
  const clean = path.length > 1 ? path.replace(/\/+$/, "") : path;
  return TITLES[clean] ?? "Админ панель";
}

export function isActivePath(itemPath: string, current: string): boolean {
  if (itemPath === "/admin") return current === "/admin" || current === "/admin/";
  return current === itemPath || current.startsWith(itemPath + "/");
}
