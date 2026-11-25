# Исправления по код-ревью 2026-11-25: план

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Исправить все находки код-ревью от 2026-11-25 (подкаталоги, опасное удаление, циклы каталогов, slug, 500 на плохих параметрах, N+1, мусорные файлы, мёртвый код, вывод текста через v-html), чтобы проект можно было передать без доработок.

**Architecture:** Бэкенд: небольшие модули-помощники (`api/categories.py`, `api/slugs.py`, `api/params.py`, `api/signals.py`) и точечные правки во views/serializers/models + две миграции. Фронт: общие утилиты `src/utils/slug.ts` и `src/utils/richText.ts` вместо пяти копий транслитерации и четырёх `formatContent`.

**Tech Stack:** Django 5.2, DRF 3.17, SQLite; Vue 3 + TypeScript, Vite; тесты фронта утилит — встроенный `node:test` (Node ≥ 22.18, без новых зависимостей).

**Spec:** код-ревью в чате 2026-11-25 (находки 1–8 и рекомендации 1–4).

## Global Constraints

- Новых зависимостей ни на бэкенде, ни на фронте.
- Сообщения для администратора — по-русски, в поле `detail` ответа (фронт уже показывает `e.response.data.detail`).
- Неверные параметры запроса: 400, никогда 500.
- Все существующие 145 тестов остаются зелёными; `makemigrations --check` — «No changes detected»; `npm run build` проходит.
- Коммиты не делаются из Linux-окружения (в рабочей копии Windows CRLF); владелец коммитит сам.

## Review Focus

1. Уже существующие в базе записи с пустым slug (созданы до исправления) — миграция данных заполняет их уникальными slug.
2. В базе уже есть цикл каталогов (A→B→A) — обход поддерева завершается, сайт не падает.
3. Удаление подкаталога с товарами при пустом родителе — запрещено с понятным сообщением.
4. Узбекская кириллица («Ўзбек қовун») и латиница с апострофом («O‘zbekiston») — непустой slug на бэкенде и на фронте.
5. Замена картинки каталога — старый файл удалён, новый на месте; удаление товара удаляет файлы всех его картинок.

---

### Task 1: Обход поддерева каталогов без рекурсии и защита от циклов

**Files:**
- Create: `back/api/categories.py`
- Modify: `back/api/models.py` (`Category.get_all_products`), `back/api/views.py:298-317` (`collect_category_ids`), `back/api/serializers.py:312` (`CategoryAdminSerializer`), `Front/src/views/CategoriesManagement.vue:252-255`
- Test: `back/api/test_categories.py`

**Interfaces:**
- Produces: `subtree_ids(root_ids: Iterable[int]) -> list[int]` — корни + все потомки, один запрос на уровень, посещённые не повторяются. `CategoryAdminSerializer.validate_parent(value)` — 400, если `value` — сам каталог или его потомок.

- [ ] Тесты: `test_subtree_includes_grandchildren`, `test_subtree_terminates_on_existing_cycle` (цикл создан через `.update()`), `test_products_filter_on_cycle_is_200`, `test_parent_cannot_be_self` (400), `test_parent_cannot_be_descendant` (400, текст содержит «подкаталог»), `test_parent_can_be_unrelated` (200).
- [ ] Запуск: падают.
- [ ] Реализация; фронт: `availableParents` исключает сам каталог и всех его потомков (по полю `parent` в `allCategories`).
- [ ] Запуск: зелёные.

### Task 2: Подкаталоги открываются через публичный API

**Files:** Modify `back/api/views.py:472-492` (`CategoryViewSet.get_queryset`). Test: `back/api/test_categories.py`

- `list`: только корневые + `?limit`; остальные действия (`retrieve`, `products`, `brands`, `tags`): все каталоги, без среза.

- [ ] Тесты: `test_child_detail_200`, `test_child_products_brands_tags_200`, `test_list_shows_only_roots`, `test_limit_ignored_on_detail` (200).
- [ ] Падают → реализация → зелёные.

### Task 3: Безопасное удаление каталогов и брендов

**Files:**
- Modify: `back/api/models.py:12,62` (`on_delete=models.PROTECT`), `back/api/views.py` (`CategoryAdminViewSet`, `BrandAdminViewSet`), `Front/src/views/BrandsManagement.vue:366-380`, `Front/src/views/CategoriesManagement.vue` (текст окна удаления)
- Create: миграция `0041_protect_category_delete.py`
- Test: `back/api/test_safe_delete.py`

**Interfaces:** `ProtectedDeleteMixin.destroy` → при `ProtectedError` ответ 400 `{"detail": <сообщение>}`; сообщение называет число товаров/подкаталогов.

- [ ] Тесты: `test_category_with_products_not_deleted` (400, товар на месте, «товар» в detail), `test_category_with_children_not_deleted` (400, «подкаталог»), `test_subcategory_with_products_blocked_even_if_parent_empty`, `test_empty_category_deleted` (204), `test_brand_with_products_not_deleted` (400, «товар»), `test_empty_brand_deleted` (204).
- [ ] Падают → реализация + `makemigrations api` → зелёные; фронт бренда показывает `detail`.

### Task 4: Уникальные slug с транслитерацией (бэк + фронт)

**Files:**
- Create: `back/api/slugs.py`, миграция `0042_fill_empty_slugs.py` (RunPython), `Front/src/utils/slug.ts`, `Front/src/utils/slug.test.ts`
- Modify: `save()` у `Category`, `Brand`, `Product`, `NewsItem`, `Tag`; `ProductAdminViewSet._create/_update`; 5 копий транслитерации на фронте (`ProductFormModal.vue`, `CategoriesManagement.vue`, `BrandsManagement.vue`, `NewsManagement.vue`, `TagsManagement.vue`)
- Test: `back/api/test_slugs.py`

**Interfaces:**
- `transliterate(text: str) -> str` (русская + узбекская кириллица: ў→o, қ→q, ғ→g, ҳ→h; апострофы ‘ ’ ʻ ` ' удаляются);
- `make_slug(text: str, max_length: int) -> str` (никогда не пустой: запасной вариант `"item"`);
- `unique_slug(model, text: str, max_length: int, exclude_pk=None) -> str` (суффиксы `-2`, `-3`, …);
- фронт: `export function makeSlug(text: string): string` — тот же алфавит.
- Создание товара: занятый slug → автоматически суффикс. Изменение товара: slug занят другим товаром → 400 «Адрес (slug) «x» уже занят другим товаром».

- [ ] Тесты бэка: `test_cyrillic_name_gets_ascii_slug` («Камеры» → `kamery`), `test_uzbek_letters` («Ўзбек қовун» → `ozbek-qovun`), `test_latin_apostrophe` («O‘zbekiston» → `ozbekiston`), `test_duplicate_names_get_suffix` (`kamera-x`, `kamera-x-2`), `test_admin_create_duplicate_slug_201`, `test_admin_update_to_taken_slug_400`, `test_symbols_only_name_not_empty`, `test_migration_fills_empty_slugs` (через функцию миграции).
- [ ] Тест фронта: `node --test Front/src/utils/slug.test.ts` — те же пять входов.
- [ ] Падают → реализация → зелёные.

### Task 5: Неверные параметры → 400, а не 500

**Files:**
- Create: `back/api/params.py`
- Modify: `back/api/views.py` — `features_tags_by_category`, `feature_values_by_feature`, `get_queryset` всех админских ViewSet с числовыми фильтрами (`category`, `brand`, `parent`, `tag_name`, `feature`, `product`, `rating`), `OrderViewSet.get_queryset` + `export_orders_csv` (общая функция), `ProductAdminViewSet._create/_update` (inline-списки и обязательные поля), `ProductViewSet.price_range` (0 ≠ None)
- Test: `back/api/test_params.py`

**Interfaces:** `int_param(params, name: str) -> int | None`, `date_param(params, name: str) -> date | None` — бросают `rest_framework.exceptions.ValidationError({name: "..."})`; `filter_orders(qs, params) -> QuerySet`; `inline_list(data, key: str) -> list[dict]`.

- [ ] Тесты: `test_orders_bad_date_400`, `test_csv_bad_date_400`, `test_orders_good_date_filters`, `test_features_tags_bad_id_400`, `test_feature_values_bad_id_400`, `test_admin_list_bad_numeric_filter_400` (subTest по всем эндпоинтам), `test_product_features_not_list_400`, `test_product_without_name_400`, `test_product_without_category_400`, `test_price_range_zero`.
- [ ] Падают → реализация → зелёные.

### Task 6: Списки товаров без N+1

**Files:** Modify `back/api/views.py` (общий `with_list_relations(qs)` для `ProductViewSet`, `CategoryViewSet.products`, `BrandViewSet.products`, `similar_products`; контекст `request` в сериализатор). Test: `back/api/test_performance.py`

- [ ] Тест: `test_product_list_query_count` — 12 товаров с картинками, брендом, группой тегов; `/api/products/` укладывается в ≤ 10 запросов; так же `/api/categories/<slug>/products/` и `/api/brands/<slug>/products/`.
- [ ] Падает (сейчас 62) → реализация → зелёный.

### Task 7: Удаление файлов картинок с диска

**Files:** Create `back/api/signals.py`; Modify `back/api/apps.py` (`ready()` импортирует signals). Test: `back/api/test_media_cleanup.py`

**Interfaces:** обработчики `post_delete` и `pre_save` для `Image.image`, `Category.image`, `Brand.logo`, `Banner.image`; удаление файла — через `transaction.on_commit`.

- [ ] Тесты (временный `MEDIA_ROOT`): `test_deleting_image_removes_file`, `test_deleting_product_removes_its_image_files`, `test_replacing_category_image_removes_old_file_keeps_new`, `test_saving_without_change_keeps_file`, `test_delete_image_endpoint_removes_file`.
- [ ] Падают → реализация → зелёные.

### Task 8: Мёртвый код

**Files:** Modify `back/api/views.py` (удалить `admin_login`, `FeatureAdminViewSet.debug_first`, неиспользуемые импорты), `back/api/serializers.py` (`LoginSerializer`), `Front/src/api/admin.ts:479` (`debugFirst`).

- [ ] Тест: `test_debug_first_removed` — `/api/admin/features/debug_first/` → 404.
- [ ] Полный прогон тестов и сборка фронта.

### Task 9: Вывод текста без HTML-инъекций и мелочи фронта

**Files:**
- Create: `Front/src/utils/richText.ts`, `Front/src/utils/richText.test.ts`
- Modify: `AboutPage.vue`, `NewsDetailPage.vue`, `Brand.vue`, `ProductDetailPage.vue` (вместо локальных `formatContent`), `stores/useCartStore.ts` (количество 1…999), `README.md` («Известные ограничения» — v-html больше не исполняет HTML)

**Interfaces:** `export function textToHtml(text: string | null | undefined): string` — экранирует `& < > " '`, затем `\n` → `<br>`; `export function truncateText(text: string, max: number): string`.

- [ ] Тест: `node --test Front/src/utils/richText.test.ts` — `<script>` экранирован, перенос → `<br>`, `null` → `""`, обрезка не режет посреди сущности.
- [ ] Падает → реализация → зелёный; `npm run build`.

### Task 10: Списки показывают все записи (найдено при выполнении Task 1)

Админские списки без переключения страниц (каталоги, бренды, теги, группы тегов, новости, картинки, сообщения, отзывы, вопросы) и публичный список корневых каталогов отдавали только первые 12 записей (пагинация DRF по умолчанию). Тринадцатый бренд нельзя было выбрать в карточке товара, тринадцатое сообщение клиента не было видно.

**Files:** Modify `back/api/pagination.py` (`LargeListPagination`: `page_size = 1000`, `page_size_query_param = "page_size"`, `max_page_size = 1000` — формат ответа `{count, next, previous, results}` не меняется), `back/api/views.py` (эти ViewSet + `CategoryViewSet`), `Front/src/views/NewsPage.vue` (`page_size: 100`). Test: `back/api/test_admin_lists.py`

- [ ] Тесты: `test_admin_lists_return_all_items` (subTest по 9 эндпоинтам, 15 записей → 15 в `results`), `test_public_root_categories_all` (15 корневых → 15), `test_header_limit_still_works` (`?limit=5` → 5).
- [ ] Падают → реализация → зелёные.

### Финальная проверка
- [ ] `DEBUG=True python manage.py test api config` — всё зелёное; `makemigrations --check --dry-run` — No changes.
- [ ] `npm run build`; `node --test src/utils/*.test.ts`.
- [ ] Запуск в режиме контейнера (entrypoint + gunicorn) и ручная проверка: подкаталог, удаление, загрузка картинки.
- [ ] Повторное код-ревью всего проекта; новые находки → новый план.
