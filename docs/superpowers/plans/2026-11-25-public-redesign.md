# Публичный сайт: редизайн и игра «Соберите систему» — план

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** новый узнаваемый вид публичной части и игра «Соберите систему» на главной, которая приводит к заявке «на расчёт».

**Architecture:** публичные стили раскладываются из `main.css`/`mobile-improvements.css` по файлам `src/styles/site/`; новые
значения токенов действуют только внутри корневого класса `.site` (админка их не видит); «лицо» (шапка, подвал, кнопки,
карточка товара, главная) переписывается, остальные страницы правятся. Логика игры — чистый TS-модуль с тестами,
компонент только рисует и перетаскивает.

**Tech Stack:** Vue 3, Vite, TypeScript, node:test, `@fontsource-variable/onest`, Pointer Events.

**Spec:** `docs/superpowers/specs/2026-11-25-public-redesign-design.md`

## Global Constraints
- Админка не меняется: поэлементные снимки 14 страниц админки и входа до/после совпадают (кроме данных).
- В `.vue` нет стилей (`tests/styles-location.test.ts`).
- Контраст ≥ 4.5:1; кнопки/ссылки-кнопки ≥ 40 px; видимый `:focus-visible`; `prefers-reduced-motion`; 375 px — `scrollWidth <= innerWidth`.
- Палитра: `#F3F5F2` бумага, `#FFFFFF` поверхность, `#D7DDD8` линия, `#111A15` чернила, `#1B4332` лес, `#F2B705` сигнал (только фон, текст на нём — чернила), `#B42318` ошибка. Без градиентов, «звёзд», золота, капс-подписей, бегущих строк.
- Шрифт Onest variable из npm, шкала 14/16/18/24/32/48 px, цены `tabular-nums`.
- Не добавлять обещаний, которых нет в текущих текстах сайта.
- `npm run build`, `npm test`, бэкенд-тесты зелёные.

## Review Focus
1. Палец на телефоне: перетаскивание фигурки не должно прокручивать страницу, а прокрутка вне фигурок — работать (`touch-action: none` только на фигурках). Проверка руками на 375 px, Task 6.
2. Бросок мимо сцены или на занятое/неподходящее место — фигурка возвращается, состояние не портится (тест модели, Task 4).
3. Длинное сообщение-заявка: текст для формы не длиннее 3000 символов (лимит бэкенда) (тест, Task 4).
4. Длинные названия товаров и большие цены — карточка не разъезжается, 2 строки названия, цена в одну строку (проверка 1280/375, Task 3).
5. Админка случайно перекрашена новыми токенами — снимки админки (Task 0 → финал).

---

### Task 0: Снимки «до»
- [ ] Поэлементные подписи (как в прошлой работе, 1280×800) для 14 страниц админки + `/admin/login` → `localStorage.__oldmap_admin`.
- [ ] Скриншоты публичных страниц 1280 и 375 (главная, каталог, раздел, товар, корзина) для отчёта.

### Task 1: Стили публичной части — по файлам (без изменения вида)
**Files:** Create `src/styles/site/*.css` (по разделам `main.css`: tokens, base, layout, typography, utilities, animations, header, footer, buttons, product-card, category-card, brand-card, news-card, forms, alerts, badges, modals, pagination, tables, brands-slider, gallery, price-filter, home, catalog, category-products, brands, pages, product-detail, favorites-compare, cart, mobile), `src/styles/site/index.css` (импорты в исходном порядке); Delete `src/styles/main.css`, `src/styles/mobile-improvements.css`; Modify `src/main.ts`, `tests/admin-styles.test.ts`.
**Interfaces:** Produces: `src/styles/site/index.css` — единственная точка входа публичных стилей; порядок каскада прежний.
- [ ] Тест `tests/site-styles.test.ts`: `main.css` и `mobile-improvements.css` не существуют; `site/index.css` импортирует только существующие файлы; ни один файл в `styles/site/` не длиннее 900 строк (поэтому `mobile-improvements.css`, 2042 строки, тоже режется по своим разделам в `site/mobile-*.css`, импорты последними).
- [ ] RED → разрезать скриптом по комментариям-разделам (разделы `mobile-improvements.css` — в `site/mobile-*.css`, после остальных) → GREEN.
- [ ] `admin-styles.test.ts` проверяет `styles/site/*.css` вместо двух старых файлов.
- [ ] Проверка: публичные 7 страниц и админка поэлементно SAME (1280).

### Task 2: Токены, шрифт, основа
**Files:** Create `src/styles/site/theme.css` (новые значения под `.site`), Modify `src/App.vue` (класс `site` на корне, когда не админка), `package.json` (+`@fontsource-variable/onest`), `src/main.ts` (импорт шрифта).
**Interfaces:** Produces: класс `.site`; переменные `--site-paper, --site-surface, --site-line, --site-ink, --site-muted (#4F5B54), --site-forest, --site-signal, --site-danger, --site-radius-card: 10px, --site-radius-ctl: 8px, --site-max: 1240px`; существующие `--primary`, `--font-sans`, `--font-display`, `--gray-*` переопределены внутри `.site`.
- [ ] Тест в `site-styles.test.ts`: `theme.css` объявляет все `--site-*` выше; в публичных файлах нет `text-transform: uppercase` у подписей-«бровей» (`.section-label`, `.hero-badge`) и нет `linear-gradient` в `site/header.css`, `site/buttons.css`, `components/HeaderComponent.css`.
- [ ] Проверка: админка SAME; публичные страницы светлые, шрифт Onest.

### Task 3: «Лицо»: шапка, подвал, нижнее меню, кнопки, карточка товара
**Files:** Modify `src/styles/site/{header,footer,buttons,product-card}.css`, `src/styles/components/{HeaderComponent,BottomNav}.css`; разметку `.vue` — только если без неё нельзя (подписи, лишние декоративные элементы).
- [ ] Шапка: белая, логотип, кнопка «Каталог», поиск, иконки с `aria-label`. Телефона в шапке сейчас нет и источника данных в шапке нет — не добавляем (контакты остаются в подвале и на странице «Контакты»).
- [ ] Карточка: рамка 1 px, без тени, фото на `--site-paper`, название 2 строки (`line-clamp`), цена одной строкой, кнопка корзины ≥ 40 px.
- [ ] Проверка: 1280/375; длинное название и цена 9 999 999 UZS (Review Focus 4); Tab по шапке.

### Task 4: Модель игры (TDD)
**Files:** Create `src/components/builder/model.ts`, `src/utils/contactPrefill.ts`; Test `tests/builder.test.ts`, `tests/contactPrefill.test.ts`.
**Interfaces:** Produces:
- `type PieceId = "dome" | "bullet" | "nvr" | "poe" | "router" | "wifi" | "access" | "ups"`
- `PIECES: { id: PieceId; label: string; search: string; img: string }[]` (8 шт., `search` — запрос для `/catalog?search=`, `img` — `/builder/<id>.png`)
- `SLOTS: { id: string; label: string; accepts: PieceId[]; x: number; y: number }[]` (x, y — % сцены)
- `type Placement = Record<string, PieceId>` (slotId → piece)
- `place(p: Placement, slotId: string, piece: PieceId): Placement` — новый объект; занятое/неподходящее/несуществующее место → тот же объект без изменений
- `removeAt(p: Placement, slotId: string): Placement`
- `firstFreeSlot(p: Placement, piece: PieceId): string | null`
- `summary(p: Placement): { id: PieceId; label: string; count: number }[]` (порядок как в `PIECES`, без нулей)
- `hints(p: Placement): string[]` — «Камерам нужен видеорегистратор…», «…PoE-коммутатор…», «Добавьте ИБП…»
- `requestText(p: Placement): string` — «Здравствуйте! Хочу рассчитать систему:\n— Купольная камера × 3\n…»
- `contactPrefill(state: unknown): string` в `contactPrefill.ts` — строка из `state.message` (`history.state`), обрезанная до 3000, иначе `""`. Не через адрес страницы: длинный `?message=` при перезагрузке упрётся в лимит длины строки запроса gunicorn (4094 байта) и даст ошибку 400.
- [ ] Тесты: place/remove неизменяемы; занятое место не перезаписывается; камера в слот для регистратора не встаёт; `firstFreeSlot` по порядку `SLOTS`, `null` если всё занято; `summary` считает и упорядочивает; три подсказки появляются и исчезают; `requestText` пустой системы — `""`; `contactPrefill({message: "x".repeat(5000)}).length === 3000`; `contactPrefill({message: ["a"]}) === ""`; `contactPrefill(null) === ""`.
- [ ] RED → реализация → GREEN; `npm test`.

### Task 5: Картинки для игры (ChatGPT в Chrome владельца)
**Files:** Create `Front/public/builder/{scene,dome,bullet,nvr,poe,router,wifi,access,ups}.png` (или `.webp`).
- [ ] Один стиль на все промпты: изометрия, мягкий «глиняный» 3D, светлые нейтральные цвета + лесной зелёный `#1B4332`, без текста и логотипов; фигурки — на чисто белом фоне (ChatGPT часто рисует «шахматку» вместо прозрачности), сцена — 16:10.
- [ ] Скачать в «Загрузки» (Chrome сохраняет туда; доступ к папке — один запрос разрешения владельцу), скопировать в `public/builder/`; Pillow: белый фон фигурок → прозрачный, фигурки ≤ 320 px, сцена ≤ 1600 px.
- [ ] После картинки сцены — поправить `x, y` в `SLOTS` под неё (тесты координаты не фиксируют).
- [ ] Если ChatGPT недоступен или стиль не держится — нарисовать SVG сами (Ruling в журнале).

### Task 6: Компонент игры и главная
**Files:** Create `src/components/builder/BuildSystem.vue`, `src/styles/components/BuildSystem.css`; Modify `src/views/HomePage.vue` (+`src/styles/views/HomePage.css`), `src/components/ContactFormComponent.vue` (префилл через `contactPrefill(history.state)`).
**Interfaces:** Consumes Task 4 целиком; картинки Task 5.
- [ ] Перетаскивание Pointer Events (`setPointerCapture`), подсветка подходящих мест, возврат при промахе; `touch-action: none` только на фигурках.
- [ ] Клавиатура: фигурка — `<button>`, Enter ставит в `firstFreeSlot`; у поставленной — кнопка «Убрать» (`aria-label`); итог в `aria-live="polite"`.
- [ ] Панель «Ваша система»: `summary`, `hints`, «Отправить на расчёт» → `router.push({ path: "/contact", state: { message: requestText(p) } })`; `ContactFormComponent` берёт `contactPrefill(history.state)`; ссылки «в каталоге» → `/catalog?search=…`.
- [ ] Анимация «встала на место» 200 ms, выключена при `prefers-reduced-motion`.
- [ ] Главная: заголовок + игра; слайдер баннеров остаётся (им управляет админка, раздел «Баннеры») — сразу под игрой; категории; услуги (тексты с текущей главной); бренды без бегущей строки; заявка. Блок «Новинки» — только если `productsAPI.getAll` уже умеет сортировку и размер страницы, иначе не добавляем (Ruling). Убрать звёздный фон и капс-подписи.
- [ ] Проверка: мышью и пальцем (375), с клавиатуры; форма контактов заполнена после «Отправить на расчёт».

### Task 7: Каталог, раздел с фильтрами, товар
**Files:** `src/styles/site/{catalog,category-products,price-filter,pagination,gallery,product-detail}.css`, `src/styles/views/{CatalogPage,ProductDetailPage}.css`.
- [ ] Фильтры: на 375 — выезжающая панель работает; цена/наличие/кнопка «в корзину» на товаре видны без прокрутки на 1280.
- [ ] Проверка: поиск, фильтр, пагинация, добавить в корзину — работают.

### Task 8: Остальные страницы
**Files:** `src/styles/site/{cart,favorites-compare,brands,pages,news-card}.css`, `src/styles/views/{AllBrandsPage,Brand,ContactPage}.css`.
- [ ] Корзина (пустая и с товарами, оформление заявки), избранное, сравнение, бренды, бренд, новости, новость, о компании, контакты, 404.

### Финал
Коммитов по ходу нет: владелец просит коммит/пуш отдельно.

- [ ] Удалить неиспользуемые правила-«украшения» (звёзды, marquee, свечения) из `styles/site/`.
- [ ] `npm run build`, `npm test`, бэкенд-тесты; админка SAME со снимком Task 0; публичные 1280/375 без горизонтальной прокрутки; Tab; контраст.
- [ ] `/engineering:code-review` по всем изменениям.
