# Паритет с shop.nag.uz, фильтры, чистка и стиль кода — план

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** покупатель получает на сайте те же возможности, что на shop.nag.uz (фильтры со счётчиками, наличие, скидки, ярлыки, документы, сопутствующие товары, вкладки на главной, акции, страницы «Покупателям»), код очищен от пустого функционала и приведён к единому стилю.

**Architecture:** бэкенд получает один модуль фильтрации каталога (`api/catalog.py`): разбор параметров → фильтр товаров → группы фильтров со счётчиками; все списки товаров (раздел, бренд, поиск, акции) идут через `GET /api/products/` и `GET /api/products/facets/`. Теги переносятся миграцией в характеристики и удаляются. Фронт хранит состояние фильтров в адресе (`utils/catalogQuery.ts`, чистый модуль с тестами) и показывает все списки одним компонентом `ProductListing.vue`.

**Tech Stack:** Django 5.2 + DRF 3.17 + SQLite, Vue 3 + Vite + TypeScript, node:test, Prettier, ESLint 9 (flat), Ruff.

**Spec:** `docs/superpowers/specs/2026-11-26-nag-parity-design.md`

## Global Constraints
- Код, тексты, вёрстка и стили shop.nag.uz не копируются; берутся только возможности из спеки.
- Рабочая копия Windows: файлы с CRLF остаются с CRLF (правки через `dev-tools/edit.py`, Prettier `endOfLine: "auto"`, Ruff `line-ending = "auto"`).
- В `.vue` нет стилей (`tests/styles-location.test.ts`); публичные стили — в `src/styles/site/`, админские — в `src/styles/admin/`; палитра и токены `.site` из спеки 25.11 не меняются; цвета логотипа не использовать.
- Админка выглядит как сейчас (новые поля — в существующих классах форм).
- Тексты на сайте — только русские; за компанию ничего не выдумывать (тексты страниц «Покупателям» заполняет владелец).
- После каждой задачи: `sh dev-tools/t.sh` → `OK`, `sh dev-tools/fe.sh` → `build=0`, `# fail 0`; с Task 2 ещё `npm run lint` и `ruff check .` без ошибок.
- Коммит — только когда владелец попросит; шаги «Commit» = `git add` нужных файлов, коммит одним разом в конце по просьбе.
- Новые миграции: `0043_product_commerce`, `0044_feature_filters`, `0045_tags_to_features`, `0046_drop_tags`, `0047_product_documents`, `0048_infopage` (номера — по порядку задач).

## Review Focus
1. Раздел без товаров/без характеристик и бренд без товаров: `/facets/` отдаёт пустые списки и `total: 0`, страница показывает «Товары не найдены» и «Сбросить фильтры», не ошибку — тест в Task 5.
2. Мусор и устаревшие параметры в адресе (`f999=abc`, `price_min=abc`, `per_page=7`, `page=999`, старые `tag=`, `ordering=`): игнорируются или приводятся к допустимым, страница за пределами — последняя существующая — тесты в Task 5 (бэкенд) и Task 6 (разбор адреса).
3. Цены: `price` пустая при заданной `old_price`, `old_price <= price` → скидки нет, карточка «Цена по запросу» — тест в Task 3 (сериализатор) и Task 6 (`priceView`).
4. Значения числовых характеристик вида «до 100», «N/A», «10 000 000», «1,5» — число берётся по правилу `parse_number`, нечисловые не ломают диапазон и не выкидывают товары, пока диапазон не выбран — тесты в Task 4 и Task 5.
5. Перенос тегов: группа без каталога, группа с тем же именем, что уже есть характеристика, тег без товаров, одинаковые названия тегов — без IntegrityError, привязки товаров сохранены — тесты в Task 4b.

---

### Task 1: Убрать пустой функционал
**Files:**
- Delete: `Front/src/views/AllBrand.vue`, `Front/src/views/AdminPanel.vue`, `Front/src/components/BrandsSlider.vue`, `CategoryCardComponent.vue`, `ProductCardComponent.vue`, `Front/src/composables/useApi.ts`, `useTheme.ts`, `Front/src/stores/app.ts`, `loading.ts`, `Front/src/utils/cache.ts`, `Front/src/i18n.ts` + их CSS-файлы, если на них ссылались только удаляемые компоненты.
- Modify: `Front/src/main.ts` (без i18n), `Front/package.json` (удалить `lodash-es`, `motion`, `vue-i18n`), `Front/src/api/index.ts` (удалить каждую экспортируемую функцию без вызовов: `categoriesAPI.getPriceRange`, `getFeatured`, `productsAPI.create/update/delete/getByFeatureValue/getByBrand`, `ordersAPI.getById/list`, `brandsAPI.getById/getTags` и др. — критерий: `grep` по `src` не находит вызова), `Front/src/types/index.ts` (типы без использований).
- Modify: `back/api/filters.py` (удалить `ProductFilter`), `back/api/serializers.py` (удалить `PriceRangeSerializer`, `ProductDetailSerializer.create/update/_save_features`, writable-поля `category_id`/`brand_id` у публичного сериализатора), `back/requirements.txt` (удалить `django-filter`, `django-import-export`, `diff-match-patch`, `tablib`, `python-pptx`, `lxml`, `xlsxwriter`).

- [ ] **Step 1:** для каждого удаляемого файла/функции/пакета `grep -rn` по `Front/src Front/tests back` — ноль использований (кроме самого определения). Если найдено использование — не удалять, записать в отчёт задачи.
- [ ] **Step 2:** удалить; `npm install` обновляет `package-lock.json`; пересобрать venv бэкенда (`rm -rf ~/work/venv`).
- [ ] **Step 3:** `sh dev-tools/t.sh` → OK; `sh dev-tools/fe.sh` → `build=0`, `# fail 0`; `npm ls lodash-es motion vue-i18n` → пусто.
- [ ] **Step 4: Commit** `chore: remove unused files, API helpers and dependencies`.

### Task 2: Единый стиль кода
**Files:**
- Create: `Front/eslint.config.js`, `Front/.prettierrc.json`, `Front/.prettierignore`, `back/pyproject.toml`, `back/requirements-dev.txt` (`ruff==0.8.*` — точная версия, доступная в pip на момент работы).
- Modify: `Front/package.json` (devDeps: `eslint@9`, `typescript-eslint@8`, `eslint-plugin-vue@9`, `prettier@3`; удалить `@typescript-eslint/eslint-plugin`, `@typescript-eslint/parser`; scripts `lint`: `eslint src tests`, `format`: `prettier --write "src/**/*.{ts,vue,css}" "tests/**/*.ts"`, `format:check` то же с `--check`), `NCF0110/README.md` (раздел «Стиль кода»: команды фронта и бэкенда), `dev-tools/fe.sh` (после тестов — `npm run lint`).
- Все файлы `Front/src`, `Front/tests`, `back/**/*.py` (кроме `migrations/`) — форматирование.

Настройки (решено): Prettier `{"printWidth": 100, "endOfLine": "auto", "trailingComma": "all"}`; ESLint: `js.configs.recommended`, `tseslint.configs.recommended`, `vue.configs["flat/recommended"]` с parser TS для `<script lang="ts">`; правила: `@typescript-eslint/no-explicit-any: "off"` (много ответов API без типов — не цель этой задачи), `vue/multi-word-component-names: "off"`, `no-console: ["warn", {allow: ["warn","error"]}]`, форматирующие правила vue выключены (`eslint-config-prettier` не нужен: `flat/recommended` + `vue/html-self-closing: off`, `vue/max-attributes-per-line: off`, `vue/singleline-html-element-content-newline: off`, `vue/html-indent: off`). Ruff: `line-length = 100`, `[format] line-ending = "auto"`, `[lint] select = ["E","F","I","B","UP"]`, `ignore = ["E501"]`, `exclude = ["*/migrations/*"]`.

- [ ] **Step 1:** установить, `npm run format`, `ruff format .`, `ruff check --fix .`.
- [ ] **Step 2:** `npm run lint` — исправить все ошибки руками (неиспользуемые переменные/импорты удаляются, `catch {}` пустые — с комментарием почему); предупреждения допустимы. `ruff check .` → `All checks passed!`.
- [ ] **Step 3:** проверка переводов строк: `git -c core.autocrlf=true diff --stat` не показывает файлов, изменённых целиком из-за CRLF→LF (для каждого изменённого файла: CRLF-строк до = CRLF-строк после, если файл был CRLF).
- [ ] **Step 4:** t.sh OK, fe.sh зелёный, `npm run format:check` → без файлов.
- [ ] **Step 5: Commit** `style: prettier, eslint and ruff across the code base`.

### Task 3: Товар: старая цена, наличие, статус, «рекомендуем»; мелкие исправления бэкенда
**Files:**
- Modify: `back/api/models.py` (Product), Create: `back/api/migrations/0043_product_commerce.py`
- Modify: `back/api/serializers.py`, `back/api/views.py` (ProductAdminViewSet `_create/_update/_check_lengths`, убрать `cache_page`), `back/config/settings.py`, `back/api/throttles.py`
- Test: `back/api/test_product_commerce.py`

**Interfaces — Produces:**
- `Product.old_price: Decimal|None (25,2)`, `Product.stock_quantity: int|None` (PositiveIntegerField), `Product.status: str` choices `("", "new", "promo", "sale")` default `""`, `Product.is_recommended: bool` default False, `Product.STATUS_LABELS = {"new": "Новинка", "promo": "Акция", "sale": "Распродажа"}`.
- `discount_percent(price, old_price) -> int|None` в `back/api/pricing.py`.
- Сериализаторы списка и детали отдают: `old_price`, `discount_percent`, `stock_quantity`, `status`, `status_label` (`""` если нет); админский — те же поля на запись + `is_recommended`.
- Админ-API товара принимает `old_price` (через `price_value(data, "old_price")`), `stock_quantity` (`int_param`, ≥ 0, иначе 400), `status` (вне списка → 400), `is_recommended`.

- [ ] **Step 1: тесты (падают)** — `test_discount_percent`: `(100,125)→20`, `(None,100)→None`, `(100,100)→None`, `(100,90)→None`, `(0,100)→None`, `(Decimal("82"),Decimal("100"))→18`; `test_list_serializer_fields` (новые поля в `/api/products/`); `test_admin_rejects_bad_status_and_negative_stock` (400 с ключом поля); `test_internal_sku_is_prefix_and_pk` (`Category(name="Камеры")`, товар без SKU → `internal_sku == f"KAM-{pk:05d}"`; второй товар с тем же префиксом не падает; если такой SKU уже занят вручную — суффикс `-2`); `test_public_lists_not_cached` (изменить имя каталога → следующий `GET /api/categories/` показывает новое имя; ответ без `max-age`); `test_throttle_ident_uses_num_proxies` (`NUM_PROXIES == TRUSTED_PROXY_COUNT`, `LoginRateThrottle().get_ident(request)` для XFF `"1.1.1.1, 2.2.2.2"` при 1 прокси = `"2.2.2.2"`); `test_order_accepts_out_of_stock_product` (товар `is_available=False` → заказ 201).
- [ ] **Step 2:** `sh dev-tools/t.sh api.test_product_commerce` → FAIL.
- [ ] **Step 3:** реализовать. SKU: в `Product.save` после первого `super().save()` при пустом `internal_sku` — `f"{prefix}-{self.pk:05d}"`, при занятости `-2`, `-3`…, `save(update_fields=["internal_sku"])`; случайные числа и `IntegrityError` удалить. Убрать все `@method_decorator(cache_page(...))`. В `REST_FRAMEWORK` добавить `"NUM_PROXIES": TRUSTED_PROXY_COUNT` (определение `TRUSTED_PROXY_COUNT` поднять выше `REST_FRAMEWORK`); удалить `RealClientIPMixin` (DRF `get_ident` даёт то же); обновить комментарии.
- [ ] **Step 4:** весь t.sh → OK (старые тесты на `RealClientIPMixin`/кеш — переписать на новое поведение, не удалять проверку подмены XFF).
- [ ] **Step 5: Commit** `feat(back): old price, stock, status, recommended; sequential SKU; no public cache; one client-IP rule`.

### Task 4: Характеристики: группа, порядок, вид фильтра, число; перенос тегов
**Files:**
- Modify: `back/api/models.py` (Feature, FeatureValue), Create: `back/api/numbers.py`, `migrations/0044_feature_filters.py`, `0045_tags_to_features.py`, `0046_drop_tags.py`
- Modify: `back/api/serializers.py`, `views.py`, `urls.py`, `admin.py` (убрать всё о тегах; `features_tags_by_category` → отдаёт только `features` и `feature_values`; `admin_stats` без `tags_count`), удалить `back/api/tagfilter.py`, тесты тегов переписать/удалить вместе с кодом.
- Front: удалить `TagsManagement.vue`, пункт меню и API тегов в `api/admin.ts`, блок «Группы тегов» в `ProductsManagement.vue`, карточку «Теги» на дашборде, фильтр по тегам в `CategoryProductsPage.vue` и `Brand.vue` (до Task 7 в разделе остаются цена, бренды, наличие), чипы тегов в `ProductCard.vue`; эндпоинты `/categories/<slug>/tags/`, `/brands/<slug>/tags/`, `/tags/` удаляются; `FeaturesManagement.vue` — поля «Группа», «Порядок», «Вид в фильтре», «Единица».
- Test: `back/api/test_features_filters.py`, `back/api/test_tags_migration.py`; `Front/tests/admin-menu.test.ts`, `dashboard.test.ts` (обновить ожидания).

**Interfaces — Produces:**
- `Feature.group: str` (100, blank), `Feature.order: int` (0), `Feature.filter_type: str` choices `list` «Список», `bool` «Да/Нет», `range` «Диапазон», `none` «Не показывать», default `list`; `Feature.unit: str` (20, blank).
- `FeatureValue.number: Decimal|None` (max_digits=24, decimal_places=4), заполняется в `save()` через `parse_number`.
- `parse_number(text: str) -> Decimal|None` в `back/api/numbers.py`: первое число в строке; пробелы/неразрывные пробелы между цифрами — разделители тысяч; запятая — десятичная. `"10 000 000"→10000000`, `"1,5 м"→1.5`, `"до 100"→100`, `"-20…+50"→-20`, `"N/A"→None`, `"Да"→None`.

- [ ] **Step 1 (4a): тесты** `test_parse_number` (значения выше), `test_feature_value_number_saved`, `test_admin_feature_accepts_group_order_type_unit` (неверный `filter_type` → 400) — FAIL → реализовать модель, миграцию 0044 (с `RunPython`, заполняющим `number` у существующих значений), сериализатор, админ-поля → PASS.
- [ ] **Step 2 (4b): тест миграции** `test_tags_migration.py` через `MigrationExecutor` (откат к `0044`, создать данные старыми моделями, накатить `0045`): группа «Цвет» (каталог A) с тегами «Черный», «Белый» на двух товарах → `Feature(name="Цвет", category=A)`, значения, `ProductFeature` для каждого (товар, тег); группа без каталога → каталог берётся у товара; уже есть `Feature("Цвет", A)` → значения добавляются к ней; уже есть `FeatureValue(A, "Черный")` → используется она; тег без товаров → не переносится; повторный прогон данных не создаёт дублей.
- [ ] **Step 3:** `0045_tags_to_features` (`RunPython(forward, migrations.RunPython.noop)`): для каждой `ProductTagGroup` с группой: `cat = group.category or product.category`; `feature = get_or_create(name=group.name, category=cat)`; для каждого тега `value = get_or_create(category=cat, value=tag.name)`, `feature.values.add(value)`, `ProductFeature.get_or_create(product, feature, value)`. `0046_drop_tags`: удалить `ProductTagGroup`, `Tag`, `TagName`.
- [ ] **Step 4:** убрать код тегов во всём проекте (`grep -rni "tag_group\|TagName\|tag_name\|/tags/" back Front/src` → только упоминания в миграциях); t.sh и fe.sh зелёные.
- [ ] **Step 5: Commit** `feat: feature groups and filter types; tags moved into features`.

### Task 5: Модуль фильтрации каталога и группы фильтров
**Files:**
- Create: `back/api/catalog.py`, Test: `back/api/test_catalog.py`
- Modify: `back/api/views.py` (`ProductViewSet` — через `catalog.py`, action `facets`), `urls.py`, `pagination.py`. Старые эндпоинты списков (`CategoryViewSet.products/brands`, `BrandViewSet.products/categories`, `products_by_feature_value`, `price_range`, `apply_product_filters`) живут до Task 7 — фронт ещё ходит в них.

**Interfaces — Produces:**
- Параметры запроса (одинаковые для `/api/products/` и `/api/products/facets/`): `category=<slug>` (раздел с подразделами), `brand=a,b`, `status=new,promo`, `promo=1` (status ∈ {promo, sale} или `old_price > price`), `recommended=1`, `in_stock=1`, `price_min`, `price_max`, `f<facetId>=<valueId>,<valueId>` (список и Да/Нет: ИЛИ внутри, И между группами), `f<facetId>_min`, `f<facetId>_max`, `q=<текст>` (название, описание, артикулы), `sort` ∈ {`popular`,`price`,`-price`,`new`,`name`}, `page`, `page_size` ∈ {20,40,80}.
- `@dataclass CatalogQuery` и `parse_catalog_query(params) -> CatalogQuery` — неверные значения игнорируются (не 400); не больше 10 групп характеристик; `page_size` вне списка → 20; `sort` вне списка → `popular`.
- `facet_defs(category_ids: list[int]) -> list[FacetDef]`, `FacetDef(id: int, name: str, group: str, order: int, type: str, unit: str, feature_ids: list[int])` — характеристики поддерева с `filter_type != "none"`, объединённые по `(name, filter_type)`; `id` = наименьший id в группе.
- `filter_products(q: CatalogQuery, skip: str|None = None) -> QuerySet[Product]` — `skip` ∈ `{"brand","status","price","f<id>"}` исключает свою группу (для счётчиков).
- `build_facets(q) -> dict`:
  `{"total", "price": {"min","max"}, "in_stock": int, "categories": [{"slug","name","count"}] (прямые подразделы), "brands": [{"slug","name","count"}], "statuses": [{"value","label","count"}], "features": [{"id","name","group","type":"list"|"bool","values":[{"ids":[int],"value":str,"count"}]} | {"id","name","group","type":"range","unit","min","max"}]}`. Значения с одинаковым текстом объединяются (`ids`). Группы и значения без товаров в текущей выборке отдаются со `count: 0` только если выбраны. Порядок: `order`, затем имя; значения `bool` — «Да» раньше «Нет»; список — по `number`, затем по тексту.
- Популярность: `Sum("order_items__quantity")`, без заказов = 0; при равенстве — новее раньше. Сортировка по цене — `F("price").asc(nulls_last=True)`.
- `ClampedPagination` (вместо `StandardResultsSetPagination` у товаров): страница > последней → последняя; ответ `{count, next, previous, results, page, page_size}`.

- [ ] **Step 1: тесты (падают)** — фикстура: раздел «Камеры» с подразделами «IP» и «Аналог», в обоих характеристика «Цвет» (list) и «Разрешение, Мп» (range), бренды, статусы, цены (включая пустую), заказы для популярности. Тесты: `test_or_within_and_across_groups`; `test_same_named_features_merge_on_parent`; `test_counts_exclude_own_group` (выбран бренд A → у брендов счётчики без фильтра по бренду, у цвета — с ним); `test_range_filter_and_bounds` (нечисловое значение не входит в min/max и не выкидывает товары без выбранного диапазона); `test_price_bounds_ignore_price_filter`; `test_promo_and_recommended`; `test_sort_popular_and_price_nulls_last`; `test_garbage_params_ignored` (`f999=abc`, `price_min=abc`, `page_size=7`, `sort=hack`, `tag=x`, `ordering=x` → 200, как без них); `test_page_beyond_last_returns_last`; `test_empty_category_and_brand_facets` (`total: 0`, пустые списки); `test_query_count_constant` (`assertNumQueries` для `/facets/` не растёт с 5 до 50 товаров).
- [ ] **Step 2:** `t.sh api.test_catalog` → FAIL.
- [ ] **Step 3:** реализовать `catalog.py` и подключить к `/api/products/` и `/api/products/facets/`.
- [ ] **Step 4:** t.sh OK.
- [ ] **Step 5: Commit** `feat(back): one catalog filter module with facet counts`.

### Task 6: Фронт: состояние фильтров в адресе
**Files:** Create `Front/src/utils/catalogQuery.ts`, `Front/src/utils/productView.ts`, Test `Front/tests/catalogQuery.test.ts`, `Front/tests/productView.test.ts`.

**Interfaces — Produces:**
- `type CatalogState = { brands: string[]; statuses: string[]; inStock: boolean; priceMin: number|null; priceMax: number|null; lists: Record<number, number[]>; ranges: Record<number, {min: number|null; max: number|null}>; q: string; sort: Sort; page: number; perPage: 20|40|80; view: "grid"|"list" }`, `type Sort = "popular"|"price"|"-price"|"new"|"name"`.
- `parseCatalogQuery(query: LocationQuery): CatalogState` (мусор → значения по умолчанию), `toRouteQuery(s: CatalogState): Record<string,string>` (значения по умолчанию не пишутся; ключи как в Task 5 + `per_page`, `view`), `toApiParams(s: CatalogState, fixed: Record<string,string>): Record<string,string>` (`per_page`→`page_size`), `activeChips(s, facets): {key: string; label: string}[]`, `removeChip(s, key): CatalogState`, `SORT_LABELS: Record<Sort,string>` (тексты из спеки).
- `stockLabel(p: {is_available: boolean; stock_quantity: number|null}): {text: string; tone: "ok"|"order"}`, `priceView(p): {price: string|null; old: string|null; discount: string|null}` (`"−18%"`; `price === null` → `"Цена по запросу"` в `price`, без старой цены), формат сумм — как в `ProductCard.vue` сейчас (вынести туда `formatSum`).

- [ ] **Step 1: тесты (падают)**: круговой `toRouteQuery(parseCatalogQuery(x))` для заполненного состояния; мусор (`per_page=7`, `page=-1`, `f12=a,3`, `price_min=abc`, `sort=x`) → умолчания и `lists[12] = [3]`; `toApiParams` пишет `page_size` и `f12=3,4`; чипы и снятие одного чипа; `stockLabel` для всех 4 случаев спеки; `priceView` для случаев Review Focus 3.
- [ ] **Step 2:** `npm test` → FAIL. **Step 3:** реализовать. **Step 4:** fe.sh зелёный.
- [ ] **Step 5: Commit** `feat(front): catalog state in the URL`.

### Task 7: Фронт: список товаров с фильтрами
**Files:**
- Create: `Front/src/components/catalog/ProductListing.vue`, `FacetPanel.vue`, `FacetList.vue`, `FacetRange.vue` (на основе `PriceFilter.vue`, который удаляется), `ListingToolbar.vue` (сортировка, «на странице», плитка/список, «N товаров»), `ActiveChips.vue`; стили `Front/src/styles/site/80-listing.css` (+ импорт в `site/index.css`).
- Modify: `Front/src/api/index.ts` (`productsAPI.list(params)`, `productsAPI.facets(params)`), `CategoryProductsPage.vue` (крошки, H1, подразделы, `<ProductListing :fixed="{category: slug}"/>`), `Brand.vue` (`fixed: {brand}`), `CatalogPage.vue` (поиск `?q=` → `ProductListing` с `fixed: {}`), `HeaderComponent.vue` (поиск ведёт на `/catalog?q=`), `ProductCard.vue` (режим `list`).
- Test: `Front/tests/listing-markup.test.ts` (разметка: в `ProductListing.vue` есть `Pagination`, `ListingToolbar`, `FacetPanel`; в страницах нет `localStorage` и `catalog_filters_`).

**Interfaces — Consumes:** Task 5 (`/products/`, `/products/facets/`), Task 6 (`parseCatalogQuery`, `toRouteQuery`, `toApiParams`, `activeChips`, `removeChip`).
**Produces:** `<ProductListing :fixed="Record<string,string>" :title-count="boolean" />` — читает/пишет `route.query` (`router.replace` для смены фильтров, `router.push` для страниц), грузит список и группы параллельно, старые ответы отбрасывает (счётчик запросов, как 25.11).

Поведение (решено): первые 5 групп раскрыты, остальные за кнопкой «Все фильтры (+N)»; в группе 6 значений, «Ещё N»; у значения — счётчик, значения с 0 серые и неактивные (кроме выбранных); Да/Нет — две галочки; диапазоны — два поля + ползунок, применяются через 600 мс после ввода; на телефоне панель — выезжающая шторка с кнопкой «Показать N товаров»; чипы над списком + «Сбросить все»; пусто → «Товары не найдены» + «Сбросить фильтры».

- [ ] **Step 1:** тест разметки → FAIL. **Step 2:** реализовать компоненты, подключить в 3 страницах; удалить старую логику фильтров (`PriceFilter.vue`, localStorage-фильтры, загрузку брендов в `CategoryProductsPage.vue`) и старые эндпоинты бэкенда из Task 5 вместе с их тестами (тесты поведения переносятся на `/api/products/?…`).
- [ ] **Step 3:** fe.sh зелёный + `npm run lint`.
- [ ] **Step 4:** сценарии для браузера записать в Task 11 (нужен пересобранный контейнер с новым бэкендом): выбор бренда меняет адрес и счётчики; «Назад» возвращает прежние фильтры; ссылка с фильтрами в новой вкладке показывает то же; 375 px — `scrollWidth <= innerWidth`.
- [ ] **Step 5: Commit** `feat(front): product listing with facets, chips, sort, per-page, list view`.

### Task 8: Карточка и страница товара
**Files:**
- Back: `serializers.py` (`ProductDetailSerializer`: `breadcrumbs: [{name, slug}]` от корня, `feature_groups: [{group, items: [{name, values: [str]}]}]` по `Feature.order`, пустая группа → «Общие»; `related`: доступные первыми, до 20; `documents`), Create `back/api/documents.py` (`validate_uploaded_document(file) -> tuple[bool, str|None]`), модель `ProductDocument(product FK CASCADE related_name="documents", title CharField 200, file FileField upload_to="documents/", order int)`, `Product.related = ManyToManyField("self", symmetrical=False, blank=True, related_name="related_to")`, миграция `0047_product_documents`; signals — удалять файл документа как у изображений; админ-API: `POST /api/admin/products/<id>/documents/` (`title`, `file`), `DELETE /api/admin/products/<id>/documents/<doc_id>/`, `related_ids: list[int]` в create/update (сам товар и несуществующие id → 400).
- Front: `ProductCard.vue` (наличие `stockLabel`, `priceView`, ярлык статуса, «−N%», кнопка «В корзину» всегда активна — снять блокировку 25.11 и CSS `:disabled` из `72-face-product-card.css`), `ProductDetailPage.vue` (крошки, «Артикул», «Код товара» = id с ведущими нулями до 6 знаков, наличие, цены, вкладки «Описание / Характеристики / Сопутствующие товары / Документация / Отзывы / Вопросы» — пустые вкладки «Сопутствующие» и «Документация» не показываются), `ProductsManagement.vue` (поля старая цена, количество, статус, «Рекомендуем», сопутствующие — поиск товара по названию/артикулу и список с удалением, документы — загрузка с названием и удаление), `ComparePage.vue` (характеристики по группам).
- Test: `back/api/test_product_page.py`, `back/api/test_documents.py`, `Front/tests/productView.test.ts` (дополнить).

- [ ] **Step 1: тесты (падают)**: `validate_uploaded_document` — PDF с `%PDF` ок и переименован в `<uuid>.pdf`; HTML с именем `x.pdf` — нет; DOCX/XLSX/ZIP по `PK\x03\x04`; DOC/XLS по `D0CF11E0A1B11AE1`; RAR по `Rar!`; `.exe`, `.svg`, `.html` — нет; > 20 МБ — нет. API: загрузка/удаление документа только для staff (анонимный → 401/403); удаление документа удаляет файл; `breadcrumbs` для товара в подразделе = [корень, подраздел]; `feature_groups` с пустой группой → «Общие»; `related_ids` с собственным id → 400.
- [ ] **Step 2:** FAIL. **Step 3:** реализовать. **Step 4:** t.sh и fe.sh зелёные.
- [ ] **Step 5: Commit** `feat: product page parity — stock, discounts, grouped specs, related, documents`.

### Task 9: Главная, «Акции», страницы «Покупателям»
**Files:**
- Back: модель `InfoPage(slug unique, title 200, content Text, order int, is_published bool True, updated_at)`, миграция `0048_infopage`; `GET /api/pages/` (опубликованные: `slug, title`, по `order`), `GET /api/pages/<slug>/`, админ CRUD `/api/admin/pages/` (slug — `unique_slug` от заголовка, если пустой); Test `back/api/test_infopages.py` (неопубликованная → 404 публично, видна в админ-API; slug из кириллицы).
- Front: `HomePage.vue` — вкладки «Рекомендуем» (`recommended=1`), «Новинки» (`sort=new`), «Акции» (`promo=1`), «Популярное» (`sort=popular`), по 8 товаров, пустые вкладки скрыты, ссылка «Все» ведёт на `/promo` или `/catalog?sort=…`; `views/PromoPage.vue` (`/promo`, `ProductListing :fixed="{promo: '1'}"`); `views/InfoPage.vue` (`/info/:slug`, `textToHtml`), `FooterComponent.vue` — колонка «Покупателям» из `/api/pages/`; шапка — ссылка «Акции»; админка: `PagesManagement.vue` + пункт меню «Страницы» (`adminMenu.ts`), стили в `styles/admin/` существующими классами.
- Test: `Front/tests/admin-menu.test.ts` (пункт «Страницы»), разметка роутера (маршруты `/promo`, `/info/:slug`).

- [ ] **Step 1:** тесты → FAIL. **Step 2:** реализовать. **Step 3:** t.sh и fe.sh зелёные. **Step 4: Commit** `feat: home product tabs, promo page, info pages`.

### Task 10: Уведомления вместо `alert()` в админке
**Files:** Create `Front/src/components/admin/toast.ts` (`toast.success(text)`, `toast.error(text)`; очередь `toasts: Ref<{id, text, tone}[]>`, автоскрытие 5 с), `AdminToasts.vue` (в `AdminLayout.vue`, `role="status"`/`aria-live="polite"`), стили `styles/admin/`; Modify все `views/*Management.vue`, `AdminSettings.vue`, `AdminProfile.vue`. Test `Front/tests/admin-markup.test.ts`: в `src/views` и `src/components` нет `alert(`; `toast.ts` — очередь и автоскрытие (fake timers `node:test` `mock.timers`).

- [ ] **Step 1:** тест → FAIL. **Step 2:** заменить каждый `alert(` на `toast.error(...)`/`toast.success(...)` с тем же текстом. **Step 3:** fe.sh зелёный. **Step 4: Commit** `feat(admin): toasts instead of alert()`.

### Task 11: Итоговая проверка
- [ ] t.sh → OK; fe.sh → `build=0`, `# fail 0`; `npm run lint`, `npm run format:check`, `ruff check .`, `ruff format --check .` — чисто.
- [ ] `python manage.py makemigrations --check --dry-run` → «No changes detected».
- [ ] Миграции на копии реальной базы владельца (если есть `back/db.sqlite3` с данными): копия → `migrate` → число товаров, характеристик товаров до/после переноса тегов сверено.
- [ ] Владелец пересобирает контейнер `run-ncf-local.bat`; проверка во встроенном браузере (1280×800, 375×812): раздел с фильтрами (сценарии Task 7), бренд, поиск, акции, товар (вкладки, документы, сопутствующие, «Под заказ» → корзина → заказ), главная (вкладки), страница «Покупателям», админка: товар с новыми полями, характеристики, страницы, уведомления. Админка остальное — без изменений вида.
- [ ] `docs/superpowers/HANDOFF.md` и проектный HANDOFF обновлены; отчёт владельцу: что сделано, что проверено руками, что нет.
