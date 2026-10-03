# Исправление критических уязвимостей (п. 1–4) — план реализации

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Закрыть подделку JWT, брутфорс админа, подмену цен в заказах и формульные инъекции в CSV, не меняя API для фронтенда и без миграций БД.

**Architecture:** Все секреты и флаги окружения читаются через маленький модуль `config/env.py` (чистые функции, покрыты тестами), `settings.py` только вызывает их. Лимиты логина используют встроенный `NUM_PROXIES` DRF и общий файловый кэш. Цена заказа вычисляется в `OrderSerializer.create` из `Product`; экранирование CSV — отдельная функция `api/csv_safety.py`.

**Tech Stack:** Django 5.2.5, DRF 3.15.2, djangorestframework-simplejwt 5.5.1, SQLite, `django.test.TestCase` + `rest_framework.test.APIClient`.

**Spec:** `docs/superpowers/specs/2026-10-03-security-audit.md`

## Global Constraints

- Никаких новых зависимостей в `requirements.txt` и никаких миграций.
- URL и формат запросов/ответов API не меняются: фронт (`Front/src/views/CartPage.vue`) продолжает слать `items[].{product, product_name, product_sku, price, quantity}`.
- Утёкший ключ `django-insecure-zo(g8-19uk$1amqpb5obk!@=)fdt-=mv7n3voxe-#zhz#k!0x(` не принимается никогда, даже при `DEBUG=True`.
- После Task 2 локальный запуск и тесты требуют `DEBUG=True` в окружении. Команда тестов (PowerShell, из `back/`): `$env:DEBUG="True"; python manage.py test api config -v 2`
- Все команды выполняются из папки `back/`.
- Лимит логина: `5/hour` на реальный IP (значение из `api/throttles.py`, не меняется).
- Лимиты заказа: `MAX_ORDER_ITEMS = 50`, `MAX_ITEM_QUANTITY = 999`.

## Review Focus

1. На Render между клиентом и Django больше одного прокси → при `TRUSTED_PROXY_COUNT=1` все клиенты получают один IP → админ заблокирован после 5 чужих ошибок. Ожидание: каждый клиент считается отдельно. Проверяется вручную в Task 7, шаг 5.
2. После `DEBUG=False` перестают грузиться картинки товаров. Ожидание: `/media/...` отдаётся. Тест `test_media_url_served_without_debug` в Task 2.
3. В корзине лежит товар, который админ уже удалил. Ожидание: 400 с ошибкой по позиции, заказ не создаётся частично. Тест `test_unknown_product_rejected` в Task 5.
4. Товар без цены (`price=None`, «цена по запросу»). Ожидание: заказ принимается, цена в позиции `None`. Тест `test_product_without_price_keeps_null` в Task 5.
5. Телефон `+998 90 123-45-67` в CSV. Ожидание: остаётся без апострофа. Тест `test_phone_number_unchanged` в Task 6.

---

### Task 0: Базовая точка (git + окружение + текущие тесты)

**Files:**
- Create: `.gitignore` в корне (`node_modules/`, `.venv/`, `__pycache__/`, `*.pyc`, `back/db.sqlite3`, `back/media/`, `.env`)

- [ ] **Step 1:** В корне `NCF0110-main`: `git init`, создать `.gitignore`, `git add -A`, `git commit -m "chore: baseline before security fixes"`. Ожидается: коммит без `node_modules` и `db.sqlite3` (`git show --stat HEAD | findstr sqlite` — пусто).
- [ ] **Step 2:** В `back/`: `python -m venv .venv`, `.venv\Scripts\activate`, `pip install -r requirements.txt`. Если pip не читает файл (UTF-16), пересохранить `requirements.txt` в UTF-8 и включить в коммит шага 4.
- [ ] **Step 3:** Run: `python manage.py test api -v 2`. Ожидается: все существующие тесты фильтров проходят. Записать число тестов — это базовая линия, регрессий быть не должно.
- [ ] **Step 4:** Сделать бэкап `db.sqlite3` (копия `db.sqlite3.bak` вне репо). Commit, если менялся requirements: `git commit -am "chore: requirements.txt to UTF-8"`.

---

### Task 1: Модуль чтения окружения `config/env.py`

**Files:**
- Create: `back/config/env.py`
- Test: `back/config/test_env.py`

**Interfaces:**
- Produces:
  - `LEAKED_SECRET_KEYS: frozenset[str]` — содержит утёкший ключ из Global Constraints.
  - `DEV_SECRET_KEY: str = "django-insecure-local-dev-only-not-for-production"`
  - `env_bool(name: str, default: bool, environ: Mapping[str, str] = os.environ) -> bool` — `"1","true","yes","on"` (без учёта регистра) → True; `"0","false","no","off",""` → False; отсутствие → `default`; иное значение → `ImproperlyConfigured`.
  - `env_list(name: str, default: list[str], environ: Mapping[str, str] = os.environ) -> list[str]` — split по `,`, strip, пустые выкинуть; отсутствие → копия `default`.
  - `resolve_secret_key(environ: Mapping[str, str], debug: bool) -> str`

- [ ] **Step 1: Написать падающие тесты** (`SimpleTestCase`, класс `EnvHelpersTest`):

```python
def test_env_bool_parses_variants(self):
    self.assertTrue(env_bool("X", False, {"X": "TRUE"}))
    self.assertFalse(env_bool("X", True, {"X": "off"}))
    self.assertTrue(env_bool("X", True, {}))
def test_env_bool_rejects_garbage(self):
    with self.assertRaises(ImproperlyConfigured): env_bool("X", False, {"X": "maybe"})
def test_env_list_strips_and_drops_empty(self):
    self.assertEqual(env_list("H", [], {"H": " a.com, ,b.com,"}), ["a.com", "b.com"])
def test_secret_key_required_in_production(self):
    with self.assertRaises(ImproperlyConfigured): resolve_secret_key({}, debug=False)
def test_secret_key_dev_fallback_only_in_debug(self):
    self.assertEqual(resolve_secret_key({}, debug=True), DEV_SECRET_KEY)
def test_leaked_key_rejected_even_in_debug(self):
    leaked = next(iter(LEAKED_SECRET_KEYS))
    for debug in (True, False):
        with self.assertRaises(ImproperlyConfigured):
            resolve_secret_key({"SECRET_KEY": leaked}, debug=debug)
def test_insecure_prefix_rejected_in_production(self):
    with self.assertRaises(ImproperlyConfigured):
        resolve_secret_key({"SECRET_KEY": "django-insecure-abc"}, debug=False)
def test_short_key_rejected_in_production(self):
    with self.assertRaises(ImproperlyConfigured):
        resolve_secret_key({"SECRET_KEY": "x" * 49}, debug=False)
def test_valid_key_returned(self):
    key = "k" * 50
    self.assertEqual(resolve_secret_key({"SECRET_KEY": key}, debug=False), key)
```

- [ ] **Step 2:** Run: `$env:DEBUG="True"; python manage.py test config.test_env -v 2` → FAIL (`ModuleNotFoundError: config.env`).
- [ ] **Step 3: Реализовать `config/env.py`** по Interfaces. Правила `resolve_secret_key`: ключ в `LEAKED_SECRET_KEYS` → ошибка всегда; нет ключа → `DEV_SECRET_KEY` при debug, иначе ошибка; при `debug=False` ключ с префиксом `django-insecure` или короче 50 символов → ошибка. Модуль не импортирует `django.conf.settings` (только `django.core.exceptions`).
- [ ] **Step 4:** Run тот же тест → PASS (9 tests).
- [ ] **Step 5:** `git add back/config/env.py back/config/test_env.py && git commit -m "feat(config): env helpers with secret key validation"`

---

### Task 2: Подключить env в `settings.py` + хосты + раздача медиа

**Files:**
- Modify: `back/config/settings.py:23-53` (SECRET_KEY, DEBUG, ALLOWED_HOSTS, удалить ручную проверку 40–53)
- Modify: `back/config/urls.py` (раздача медиа)
- Modify: `back/.env.example` (документация переменных)
- Test: `back/api/test_security.py` (создать)

**Interfaces:**
- Consumes: `env_bool`, `env_list`, `resolve_secret_key` из Task 1.
- Produces: настройки `DEBUG: bool`, `SERVE_MEDIA: bool`; тестовый хелпер `reload_urls() -> None` в `api/test_security.py` (используется Task 4).

- [ ] **Step 1: Падающие тесты** в `api/test_security.py`. Модульная функция `reload_urls()` = `importlib.reload(config.urls); clear_url_caches()` (urls читают настройки при импорте). Класс `HostAndMediaTest(TestCase)`, в `tearDown` вызывать `reload_urls()`:

```python
def test_unknown_host_rejected(self):
    resp = self.client.get("/api/categories/", HTTP_HOST="evil.example")
    self.assertEqual(resp.status_code, 400)
def test_media_url_served_without_debug(self):
    with override_settings(DEBUG=False, SERVE_MEDIA=True):
        reload_urls()
        self.assertEqual(resolve("/media/products/x.jpg").func, django.views.static.serve)
def test_media_not_served_when_disabled(self):
    with override_settings(DEBUG=False, SERVE_MEDIA=False):
        reload_urls()
        with self.assertRaises(Resolver404): resolve("/media/products/x.jpg")
def test_wildcard_not_in_allowed_hosts(self):
    self.assertNotIn("*", settings.ALLOWED_HOSTS)
```

- [ ] **Step 2:** Run: `$env:DEBUG="True"; python manage.py test api.test_security -v 2` → FAIL (`'*'` в хостах; при `DEBUG=False` маршрут `/media/` отсутствует).
- [ ] **Step 3: Изменить `settings.py`:**
  - `DEBUG = env_bool("DEBUG", False)`; `SECRET_KEY = resolve_secret_key(os.environ, DEBUG)`; удалить блок строк 40–53.
  - `ALLOWED_HOSTS = env_list("ALLOWED_HOSTS", ["ncb-1.onrender.com"])`, при `DEBUG` добавить `"localhost", "127.0.0.1"`, при наличии `REPLIT_DEV_DOMAIN` — его. `'*'` убрать.
  - `SERVE_MEDIA = env_bool("SERVE_MEDIA", True)`.
- [ ] **Step 4: Изменить `config/urls.py`:** заменить `if settings.DEBUG: urlpatterns += static(...)` на: если `settings.DEBUG or settings.SERVE_MEDIA` — `re_path(r"^media/(?P<path>.*)$", serve, {"document_root": settings.MEDIA_ROOT})` (хелпер `static()` при `DEBUG=False` возвращает пустой список, поэтому он не подходит).
- [ ] **Step 5:** Заполнить `.env.example`: `SECRET_KEY=`, `DEBUG=False`, `ALLOWED_HOSTS=ncb-1.onrender.com`, `SERVE_MEDIA=True`, `TRUSTED_PROXY_COUNT=1`, `ENABLE_DJANGO_ADMIN=False` — по комментарию на строку.
- [ ] **Step 6:** Run: `$env:DEBUG="True"; python manage.py test api config -v 2` → PASS, число старых тестов = базовой линии из Task 0.
- [ ] **Step 7:** Проверка прод-конфигурации: `$env:DEBUG="False"; $env:SECRET_KEY=(python -c "from django.core.management.utils import get_random_secret_key as g; print(g())"); python manage.py check --deploy`. Ожидается: нет ошибок уровня ERROR; без `SECRET_KEY` команда падает с `ImproperlyConfigured`.
- [ ] **Step 8:** `git commit -am "fix(security): require real SECRET_KEY, DEBUG off by default, explicit hosts"`

---

### Task 3: Лимит логина по реальному IP + общий кэш

**Files:**
- Modify: `back/config/settings.py` (`REST_FRAMEWORK`, новый `CACHES`)
- Test: `back/api/test_security.py` (класс `LoginThrottleTest`)

**Interfaces:**
- Consumes: `LoginRateThrottle` (`api/throttles.py`, без изменений), URL name `admin-login`.
- Produces: env `TRUSTED_PROXY_COUNT` (int, default 1), env `CACHE_DIR`.

- [ ] **Step 1: Падающие тесты** (`setUp`: `cache.clear()`; все запросы с `REMOTE_ADDR="10.0.0.1"`, неверный пароль на `reverse("admin-login")`):

```python
def test_spoofed_xff_does_not_bypass_limit(self):
    for i in range(5):
        r = self._login(xff=f"1.2.3.{i}, 203.0.113.7")
        self.assertEqual(r.status_code, 401)
    self.assertEqual(self._login(xff="9.9.9.9, 203.0.113.7").status_code, 429)
def test_other_real_client_not_blocked(self):
    for _ in range(5): self._login(xff="203.0.113.7")
    self.assertEqual(self._login(xff="203.0.113.8").status_code, 401)
def test_no_proxy_header_uses_remote_addr(self):
    for _ in range(5): self._login(xff=None)
    self.assertEqual(self._login(xff=None).status_code, 429)
```

- [ ] **Step 2:** Run: `$env:DEBUG="True"; python manage.py test api.test_security.LoginThrottleTest -v 2` → FAIL (первый тест получает 401 вместо 429).
- [ ] **Step 3:** В `REST_FRAMEWORK` добавить `"NUM_PROXIES": int(os.environ.get("TRUSTED_PROXY_COUNT", "1"))`. Добавить `CACHES = {"default": {"BACKEND": "django.core.cache.backends.filebased.FileBasedCache", "LOCATION": os.environ.get("CACHE_DIR", os.path.join(tempfile.gettempdir(), "ncf_django_cache"))}}` — общий для всех воркеров gunicorn на инстансе, без миграций.
- [ ] **Step 4:** Run тесты класса → PASS; затем весь набор `api config` → PASS (файловый кэш влияет на `cache_page` — старые тесты не должны падать; если падают из-за закэшированных ответов, добавить `cache.clear()` в `setUp` их базового класса).
- [ ] **Step 5:** `git commit -am "fix(security): throttle login by real client IP, shared cache"`

---

### Task 4: Выключить Django-админку на проде по умолчанию

**Files:**
- Modify: `back/config/settings.py` (`ENABLE_DJANGO_ADMIN`)
- Modify: `back/config/urls.py` (путь `dashboard-ctrl-panel/` только при флаге)
- Test: `back/api/test_security.py` (класс `DjangoAdminToggleTest`)

**Interfaces:**
- Consumes: `env_bool`, `DEBUG`.
- Produces: `ENABLE_DJANGO_ADMIN: bool = env_bool("ENABLE_DJANGO_ADMIN", DEBUG)`.

- [ ] **Step 1: Падающие тесты.** Использовать `reload_urls()` из Task 2 внутри `override_settings` и в `tearDown`:

```python
def test_admin_hidden_when_disabled(self):
    with override_settings(ENABLE_DJANGO_ADMIN=False):
        reload_urls()
        self.assertEqual(self.client.get("/dashboard-ctrl-panel/login/").status_code, 404)
def test_admin_available_when_enabled(self):
    with override_settings(ENABLE_DJANGO_ADMIN=True):
        reload_urls()
        self.assertEqual(self.client.get("/dashboard-ctrl-panel/login/").status_code, 200)
```

- [ ] **Step 2:** Run класс → FAIL (первый тест получает 200).
- [ ] **Step 3:** Добавить настройку; в `urls.py` включать `path("dashboard-ctrl-panel/", admin.site.urls)` только при `settings.ENABLE_DJANGO_ADMIN`.
- [ ] **Step 4:** Run класс + полный набор → PASS.
- [ ] **Step 5:** `git commit -am "fix(security): disable Django admin in production unless enabled"`

---

### Task 5: Цена, название и артикул заказа — только с сервера

**Files:**
- Modify: `back/api/serializers.py:574-602` (`OrderItemSerializer`, `OrderSerializer`)
- Modify: `back/api/views.py:1361-1364` (`OrderViewSet.get_serializer_class`)
- Test: `back/api/test_orders.py` (создать)

**Interfaces:**
- Produces: `MAX_ORDER_ITEMS = 50`, `MAX_ITEM_QUANTITY = 999` в `api/serializers.py`.
- Контракт API: вход прежний; `product_name`, `product_sku`, `price` во входе игнорируются; ответ 201 содержит серверные значения.

- [ ] **Step 1: Падающие тесты** (`setUpTestData`: категория, товар `price=Decimal("100.00")`, `manufacturer_sku="SKU-1"`; товар без цены; staff-пользователь; обычный пользователь). Хелпер `_post(items, **extra)` → `POST /api/orders/` в формате `CartPage.vue`.

```python
def test_client_price_and_name_are_ignored(self):
    r = self._post([{"product": p.id, "product_name": "Fake", "product_sku": "X", "price": "1", "quantity": 2}])
    self.assertEqual(r.status_code, 201)
    item = OrderItem.objects.get(order_id=r.data["id"])
    self.assertEqual((item.price, item.product_name, item.product_sku, item.quantity),
                     (Decimal("100.00"), p.name, "SKU-1", 2))
def test_product_without_price_keeps_null(self): ...  # 201, item.price is None
def test_item_without_product_rejected(self): ...     # product отсутствует / None → 400, Order.objects.count() == 0
def test_unknown_product_rejected(self): ...          # product=999999 → 400, Order.objects.count() == 0
def test_empty_items_rejected(self): ...              # items=[] → 400
def test_too_many_items_rejected(self): ...           # 51 позиция → 400
def test_quantity_bounds(self): ...                   # 0 → 400, 1000 → 400, 999 → 201
def test_anonymous_cannot_set_status(self): ...       # status="completed" → order.status == "new"
def test_non_staff_user_cannot_set_status(self): ...  # force_authenticate(обычный) → status == "new"
def test_staff_can_patch_status(self): ...            # staff PATCH /api/orders/{id}/ {"status": "processing"} → 200
```

- [ ] **Step 2:** Run: `$env:DEBUG="True"; python manage.py test api.test_orders -v 2` → FAIL (цена 1, пустой заказ принимается и т.д.).
- [ ] **Step 3: `OrderItemSerializer`:** `product = PrimaryKeyRelatedField(queryset=Product.objects.all())` (обязательное, без null); `quantity = IntegerField(min_value=1, max_value=MAX_ITEM_QUANTITY)`; `read_only_fields = ["product_name", "product_sku", "price"]`.
- [ ] **Step 4: `OrderSerializer`:** `validate_items(value)` — 400 при `len == 0` или `> MAX_ORDER_ITEMS`. `create()` в `transaction.atomic()`: для каждой позиции `product = item["product"]`; `OrderItem.objects.create(order=order, product=product, product_name=product.name, product_sku=product.manufacturer_sku or "", price=product.price, quantity=item["quantity"])`.
- [ ] **Step 5: `OrderViewSet.get_serializer_class`:** `OrderAdminSerializer` только если `request.user.is_staff`.
- [ ] **Step 6:** Run `api.test_orders` → PASS, затем полный набор → PASS.
- [ ] **Step 7:** Ручная проверка фронта: `npm run dev`, оформить заказ из корзины → успех; в админке «Заявки» цена совпадает с каталогом.
- [ ] **Step 8:** `git commit -am "fix(security): compute order item price on server, validate order limits"`

---

### Task 6: Экранирование ячеек в CSV-экспорте заказов

**Files:**
- Create: `back/api/csv_safety.py`
- Modify: `back/api/views.py:1434-1451` (`export_orders_csv`, все строковые колонки)
- Test: `back/api/test_csv_export.py`

**Interfaces:**
- Produces: `safe_csv_cell(value: object) -> object` — не строки возвращает как есть; строку, начинающуюся с `= + - @ \t \r`, возвращает с префиксом `'`, кроме строк, полностью совпадающих с `^\+?[0-9][0-9 ()\-]*$` (телефоны/числа).

- [ ] **Step 1: Падающие тесты:**

```python
def test_formula_prefixed(self):
    self.assertEqual(safe_csv_cell('=HYPERLINK("http://x")'), '\'=HYPERLINK("http://x")')
    self.assertEqual(safe_csv_cell("@SUM(A1)"), "'@SUM(A1)")
    self.assertEqual(safe_csv_cell("-2+3"), "'-2+3")
    self.assertEqual(safe_csv_cell("\t=1"), "'\t=1")
def test_phone_number_unchanged(self):
    self.assertEqual(safe_csv_cell("+998 90 123-45-67"), "+998 90 123-45-67")
def test_plain_text_and_non_strings_unchanged(self):
    self.assertEqual(safe_csv_cell("Иван"), "Иван"); self.assertEqual(safe_csv_cell(5), 5)
def test_export_escapes_customer_fields(self):
    # Order(customer_name='=cmd|"/c calc"!A1', comment="+SUM(1)") , staff GET reverse("export-orders-csv")
    body = resp.content.decode("utf-8-sig")
    self.assertIn("'=cmd", body); self.assertIn("'+SUM(1)", body)
def test_export_requires_staff(self):
    self.assertEqual(anon_client.get(reverse("export-orders-csv")).status_code, 401)
```

- [ ] **Step 2:** Run: `$env:DEBUG="True"; python manage.py test api.test_csv_export -v 2` → FAIL (`ModuleNotFoundError: api.csv_safety`).
- [ ] **Step 3:** Реализовать `safe_csv_cell`; в `export_orders_csv` пропустить через неё имя, телефон, email, telegram, комментарий и строку товаров (старые заказы содержат названия товаров от клиента).
- [ ] **Step 4:** Run `api.test_csv_export` + полный набор → PASS.
- [ ] **Step 5:** `git commit -am "fix(security): neutralize spreadsheet formulas in orders CSV export"`

---

### Task 7: Деплой и проверка на проде (вручную, владелец)

- [ ] **Step 1: До деплоя.** Открыть `https://ncb-1.onrender.com/api/does-not-exist/`. Жёлтая отладочная страница Django → прод работал с `DEBUG=True` и утёкшим ключом: проверить в админке список пользователей (`is_staff`), последние изменения товаров/баннеров и заказы на посторонние правки.
- [ ] **Step 2: Переменные на Render** (Environment): `SECRET_KEY` (новый, из `get_random_secret_key()`), `DEBUG=False`, `ALLOWED_HOSTS=ncb-1.onrender.com`, `SERVE_MEDIA=True`, `TRUSTED_PROXY_COUNT=1`, `ENABLE_DJANGO_ADMIN=False`. Ставятся до деплоя — без `SECRET_KEY` новый код не стартует.
- [ ] **Step 3: Деплой.** Ожидается: все админы разлогинены (старые JWT недействительны) — это нормально.
- [ ] **Step 4: Смоук-проверки:** тот же несуществующий URL → обычный 404 без трейсбека; `curl -H "Host: evil.example" https://ncb-1.onrender.com/api/categories/` → 400; картинки товаров грузятся; вход в Vue-админку работает; тестовый заказ с сайта → в админке цена из каталога; CSV-экспорт открывается в Excel.
- [ ] **Step 5: Проверка лимита:** 6 неверных входов с одного устройства → 6-й = 429; с другой сети (мобильный интернет) сразу после → 401, не 429. Если со второй сети тоже 429 — поставить `TRUSTED_PROXY_COUNT=2`, передеплоить, повторить.
- [ ] **Step 6:** Сменить пароль администратора на новый (12+ символов, нигде не использованный).
