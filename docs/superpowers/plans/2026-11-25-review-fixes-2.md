# Исправления по код-ревью, круг 2: план

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Админ всегда видит понятную причину ошибки, ничего не теряется молча (картинки, экспорт), адрес товара не меняется сам.

**Architecture:** Общий помощник `adminErrorMessage` во фронте вместо десятка `e.response?.data?.detail || "Ошибка"`; Django-сообщения на русском (`LANGUAGE_CODE = "ru"`); экспорт CSV через общий `adminApi` (с обновлением токена); загрузка картинок товара собирает ошибки.

**Tech Stack:** как в круге 1. **Spec:** второе код-ревью в чате 2026-11-25.

## Global Constraints
Как в `2026-11-25-review-fixes.md`: без новых зависимостей, 400 с полем и русским текстом, все тесты зелёные, `npm run build` и `npm test` проходят.

## Review Focus
1. Ошибка по полю, которого нет в словаре подписей — показывается само сообщение (без подписи), а не «Ошибка».
2. Ответ без тела (сеть оборвалась, 502 от прокси) — показывается запасной текст, а не `undefined`.
3. Несколько картинок, из них одна плохая — остальные загружены, админ видит имя плохого файла и причину.
4. Экспорт CSV через 20 минут после входа — файл скачивается (токен обновлён).
5. Редактирование товара со старым slug в верхнем регистре без изменения поля slug — slug не меняется.

---

### Task 1: Понятные ошибки в админке
**Files:** Modify `Front/src/utils/apiError.ts` (+ `adminErrorMessage(error: unknown, fallback: string): string`), все `*Management.vue`, `AdminSettings.vue`, `AdminProfile.vue` (catch-блоки сохранения/удаления, смена статуса заказа — теперь с сообщением); `back/config/settings.py` (`LANGUAGE_CODE = 'ru'`). Test: `Front/tests/apiError.test.ts`, `back/api/test_admin_errors.py`.
- [ ] Тесты фронта: `detail` строкой; ошибка поля `{name: ["…"]}` → «Название: …»; неизвестное поле → только текст; `non_field_errors`; вложенный список; нет `response` → fallback.
- [ ] Тест бэка: `test_duplicate_brand_name_message_in_russian` — 400, текст содержит «уже существует».
- [ ] Падают → реализация → зелёные; сборка.

### Task 2: Ошибки загрузки картинок товара не теряются
**Files:** Create `Front/src/utils/uploads.ts` (`uploadEach<T>(items: T[], upload: (item: T) => Promise<unknown>, name: (item: T) => string): Promise<string[]>` — возвращает «имя: причина» для каждой неудачи); Modify `ProductsManagement.vue`. Test: `Front/tests/uploads.test.ts`.
- [ ] Тест: из трёх загрузок вторая падает → две выполнены, одна строка с именем файла и причиной.
- [ ] Падает → реализация → после сохранения товара `alert` с перечнем неудачных файлов.

### Task 3: Экспорт CSV с обновлением токена
**Files:** Modify `Front/src/api/admin.ts` (`ordersAdminAPI.exportCsv(params: Record<string,string>)` через `adminApi`, `responseType: "blob"`), `OrdersManagement.vue` (вызов, `revokeObjectURL` после скачивания, сообщение об ошибке через `adminErrorMessage`).
- [ ] Проверка: `npm run build`; ручная проверка в режиме контейнера с истёкшим access-токеном.

### Task 4: Slug товара не меняется сам
**Files:** Modify `back/api/views.py` (`_update`: если `data['slug'] == product.slug`, не трогать). Test: `back/api/test_slugs.py`.
- [ ] Тест `test_update_keeps_existing_uppercase_slug` — товар со slug `Hik-1`, PATCH с тем же slug и новым названием → slug `Hik-1`.

### Task 5: Мелочи
**Files:** Delete `Front/src/components/ProductFormModal.vue` (нигде не используется); Modify `back/api/models.py` (`Banner.__str__` без заголовка → «Баннер #<id>»). Test: `back/api/test_admin_errors.py::test_banner_str_without_title`.

### Финальная проверка
- [ ] Все тесты бэка, `makemigrations --check`, pyflakes без неопределённых имён; `npm run build`, `npm test`; сквозная проверка в режиме контейнера; новое код-ревью.

---

## Круги 3–4 (выполнено)

Найдено при третьем ревью и автоматическом прогоне 2946 запросов с неверными параметрами и телами (все GET-эндпоинты, все POST/PATCH/PUT):

- `/api/tags/with_count/` всегда отвечал 500 (неверное имя связи) — `test_tags_with_count_200`.
- Цена `1e999`, `1e30`, отрицательная, с тремя знаками после запятой сохранялась через админку и ломала все страницы с этим товаром — `price_value()` в `api/params.py`, `ProductPriceTest`.
- Длина названия и артикулов не проверялась (SQLite не проверяет сам) — `ProductLengthTest`.
- Повтор внутреннего SKU и несуществующий бренд давали сырую ошибку базы — `ProductUniqueAndRefsTest`.
- PATCH заказа с `items` → 500 — `OrderUpdateTest`.
- Цикл каталогов через стандартную Django-админку — `Category.clean()`, `ModelCleanCycleTest`.
- Открытие сайта по IP сервера → 400: подсказка в `.env.docker.example` и README.

Итог: 210 тестов бэкенда, 17 тестов фронта, сборка, фаззинг — 0 ответов 5xx.
