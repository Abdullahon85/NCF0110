import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { adminMenu, pageTitle, isActivePath } from "../src/components/admin/adminMenu.ts";
import { ICON_PATHS } from "../src/components/admin/icons.ts";

const ADMIN_PAGES = [
  "/admin",
  "/admin/orders",
  "/admin/messages",
  "/admin/reviews",
  "/admin/questions",
  "/admin/products",
  "/admin/categories",
  "/admin/brands",
  "/admin/features",
  "/admin/banners",
  "/admin/news",
  "/admin/pages",
  "/admin/settings",
  "/admin/profile",
];

test("menu is grouped by kind of work", () => {
  assert.deepEqual(
    adminMenu.map((g) => [g.title, g.items.map((i) => i.label)]),
    [
      [null, ["Обзор"]],
      ["Работа", ["Заказы", "Сообщения", "Отзывы", "Вопросы"]],
      ["Каталог", ["Товары", "Каталоги", "Бренды", "Характеристики"]],
      ["Сайт", ["Баннеры", "Новости", "Страницы", "Настройки"]],
    ],
  );
});

test("badges only where the stats API has a counter", () => {
  const badged = adminMenu.flatMap((g) => g.items).filter((i) => i.badge);
  assert.deepEqual(
    badged.map((i) => [i.path, i.badge]),
    [
      ["/admin/orders", "orders"],
      ["/admin/messages", "messages"],
    ],
  );
});

test("every admin page has its own title, without emoji", () => {
  for (const p of ADMIN_PAGES) {
    const t = pageTitle(p);
    assert.match(t, /^[\p{L} ]+$/u, `${p} -> ${t}`);
  }
  assert.equal(new Set(ADMIN_PAGES.map(pageTitle)).size, ADMIN_PAGES.length);
});

test("every icon the layout uses exists", () => {
  const used = [
    ...adminMenu.flatMap((g) => g.items.map((i) => i.icon)),
    "menu",
    "close",
    "external",
    "logout",
  ];
  for (const name of used) assert.ok(ICON_PATHS[name], name);
});

test("active menu item matches whole path segments only", () => {
  assert.equal(isActivePath("/admin", "/admin"), true);
  assert.equal(isActivePath("/admin", "/admin/orders"), false);
  assert.equal(isActivePath("/admin/news", "/admin/news"), true);
  assert.equal(isActivePath("/admin/news", "/admin/news/5"), true);
  assert.equal(isActivePath("/admin/news", "/admin/newsletter"), false);
});

test("admin frame styles live in admin/layout.css only", () => {
  const read = (p: string) => readFileSync(new URL(p, import.meta.url), "utf8");
  const legacy = read("../src/styles/admin/legacy.css");
  for (const cls of [
    "admin-sidebar",
    "admin-header",
    "admin-main",
    "sidebar-nav",
    "user-dropdown",
    "collapse-btn",
    "mobile-overlay",
  ]) {
    assert.ok(!legacy.includes("." + cls), `legacy.css still has .${cls}`);
  }
  const layout = read("../src/styles/admin/layout.css");
  assert.match(layout, /:focus-visible/);
  assert.match(layout, /prefers-reduced-motion/);
  assert.match(
    read("../src/styles/admin/index.css"),
    /tokens\.css[\s\S]*legacy\.css[\s\S]*layout\.css/,
  );
});
