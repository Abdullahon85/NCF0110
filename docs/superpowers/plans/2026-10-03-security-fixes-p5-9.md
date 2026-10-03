# Исправление уязвимостей п. 5–9 — план реализации

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Закрыть спам в отзывах/заявках, загрузку вредоносных файлов, «вечные» refresh-токены, DoS через фильтры, уязвимые зависимости и опасные ссылки баннеров — без миграций БД и без поломки текущего фронта.

**Architecture:** Сначала обновляем зависимости (дальнейшие тесты идут уже на новых версиях). Лимит по реальному IP выносится в общий миксин `RealClientIPMixin` (из п. 2) и переиспользуется новым `PublicWriteThrottle`. Проверка картинок — отдельный модуль `api/uploads.py` (содержимое через Pillow), отзыв токенов — `api/auth.py`, проверка ссылок — `api/validators.py`. Модерация и лимиты длины — только в сериализаторах/вьюхах, без изменения моделей.

**Tech Stack:** Django 5.2 (→ 5.2.17), DRF (→ 3.17.2), SimpleJWT 5.5.1 + token_blacklist, Pillow (→ 12.3.0), Vue 3 + TypeScript (vue-tsc).

**Spec:** `docs/superpowers/specs/2026-10-03-security-audit-p5-9.md`

## Global Constraints

- Ветка `security/p5-9` создаётся от `security/p1-4` (п. 1–4 ещё не влиты в `main`); всё из п. 1–4 сохраняется.
- Никаких миграций: `python manage.py makemigrations --check --dry-run` → `No changes detected` после каждой задачи.
- Команда тестов (из `back/`): `DEBUG=True python manage.py test api config -v 2` (PowerShell: `$env:DEBUG="True"; python manage.py test api config -v 2`).
- Фронт проверяется `npm run build` в `Front/` (запускает `vue-tsc -b && vite build`) → без ошибок.
- Версии зависимостей — ровно из спецификации п. 9; `pip-audit -r requirements.txt` → `No known vulnerabilities found`.
- Лимит публичных POST: `PUBLIC_WRITE_RATE = "30/hour"` на реальный IP, общий для заказов, отзывов, вопросов и сообщений.
- Лимиты длины: `REVIEW_TEXT_MAX_LENGTH = 2000`, `QUESTION_TEXT_MAX_LENGTH = 1000`, `CONTACT_MESSAGE_MAX_LENGTH = 3000`, `ORDER_COMMENT_MAX_LENGTH = 1000`.
- Картинки: форматы `JPEG, PNG, GIF, WEBP`; `MAX_UPLOAD_SIZE = 10 * 1024 * 1024`; `MAX_IMAGE_PIXELS = 60_000_000`.
- DoS: `MAX_FEATURE_FILTERS = 10`, `MAX_BY_FEATURE_RESULTS = 100`, `MAX_LIST_LIMIT = 100`.
- Тексты для покупателя (точно): отзыв — `Спасибо! Отзыв появится после проверки модератором.`; вопрос — `Спасибо! Вопрос появится после проверки модератором.`

## Review Focus

1. Уже загруженные картинки (включая старые SVG) продолжают отображаться, а админ может менять порядок/главное фото без перезагрузки файла. Тест `test_image_admin_patch_order_still_works` в Task 5.
2. Обычное фото с телефона (JPEG 4000×3000) принимается. Тест `test_large_phone_photo_accepted` в Task 5.
3. Админ нажимает «Выйти», когда access-токен уже истёк — refresh всё равно отзывается. Тест `test_logout_without_access_token_still_revokes` в Task 6.
4. После смены пароля текущая сессия админа продолжает работать (другие — нет). Тест `test_change_password_returns_working_new_tokens` в Task 6.
5. Существующие относительные ссылки баннеров (`catalog/cameras`, `/brands`, `#promo`) по-прежнему сохраняются. Тест `test_safe_links_allowed` в Task 8.

---

### Task 0: Ветка и базовая линия

- [ ] **Step 1:** `git switch security/p1-4 && git switch -c security/p5-9`. Run: `git branch --show-current` → `security/p5-9`.
- [ ] **Step 2:** Run полную команду тестов. Expected: `Ran 57 tests ... OK` (базовая линия).
- [ ] **Step 3:** Run: `pip-audit -r requirements.txt` (pip-audit ставится в venv, не в requirements). Expected: находки по Django, Pillow, PyJWT, sqlparse, DRF, lxml, tablib — это «красный» тест для Task 1.

---

### Task 1: Обновление зависимостей (п. 9)

**Files:**
- Modify: `back/requirements.txt` (пересохранить в UTF-8 без BOM, обновить пины)

- [ ] **Step 1:** Переписать `requirements.txt` в UTF-8: `Django==5.2.17`, `djangorestframework==3.17.2`, `pillow==12.3.0`, `pyjwt==2.15.1`, `sqlparse==0.6.0`, `tablib==3.10.0`, `lxml==6.1.3`, `asgiref==3.12.1`; остальные строки — как были. Run: `python -c "open('requirements.txt',encoding='utf-8').read()"` → без ошибок.
- [ ] **Step 2:** Run: `pip install -r requirements.txt && pip check`. Expected: `No broken requirements found.`
- [ ] **Step 3:** Run: `pip-audit -r requirements.txt`. Expected: `No known vulnerabilities found`.
- [ ] **Step 4:** Run: полная команда тестов → `Ran 57 tests ... OK`; `makemigrations --check --dry-run` → `No changes detected`; `DEBUG=False SECRET_KEY=<50+ случайных> python manage.py check --deploy` → `no issues`.
- [ ] **Step 5:** `git commit -am "fix(deps): upgrade Django 5.2.17 and vulnerable dependencies; requirements.txt to UTF-8"`

---

### Task 2: ALLOWED_HOSTS — хост Render и запрет wildcard (п. 9)

**Files:**
- Modify: `back/config/env.py`, `back/config/settings.py` (блок `ALLOWED_HOSTS`)
- Test: `back/config/test_env.py`

**Interfaces:**
- Produces: `build_allowed_hosts(environ: Mapping[str, str], debug: bool) -> list[str]` в `config/env.py`. Порядок: `env_list("ALLOWED_HOSTS", ["ncb-1.onrender.com"], environ)` + `RENDER_EXTERNAL_HOSTNAME` (если задан) + `REPLIT_DEV_DOMAIN` (если задан) + `["localhost", "127.0.0.1"]` при `debug`; без дублей; `"*"` или пустой элемент → `ImproperlyConfigured`.

- [ ] **Step 1: Падающие тесты** (класс `AllowedHostsTest(SimpleTestCase)`):

```python
def test_default_production_hosts(self):
    self.assertEqual(build_allowed_hosts({}, debug=False), ["ncb-1.onrender.com"])
def test_render_hostname_added(self):
    self.assertIn("x.onrender.com", build_allowed_hosts({"RENDER_EXTERNAL_HOSTNAME": "x.onrender.com"}, False))
def test_localhost_only_in_debug(self):
    self.assertNotIn("localhost", build_allowed_hosts({}, False))
    self.assertIn("localhost", build_allowed_hosts({}, True))
def test_wildcard_rejected(self):
    with self.assertRaises(ImproperlyConfigured):
        build_allowed_hosts({"ALLOWED_HOSTS": "example.uz,*"}, False)
def test_no_duplicates(self):
    hosts = build_allowed_hosts({"ALLOWED_HOSTS": "a.uz", "RENDER_EXTERNAL_HOSTNAME": "a.uz"}, False)
    self.assertEqual(hosts.count("a.uz"), 1)
```

- [ ] **Step 2:** Run: `... test config.test_env` → FAIL (`ImportError: build_allowed_hosts`).
- [ ] **Step 3:** Реализовать `build_allowed_hosts`; в `settings.py` заменить блок `ALLOWED_HOSTS` на `ALLOWED_HOSTS = build_allowed_hosts(os.environ, DEBUG)`.
- [ ] **Step 4:** Run полную команду тестов → OK (существующий `test_unknown_host_rejected` тоже зелёный).
- [ ] **Step 5:** `git commit -am "fix(security): build ALLOWED_HOSTS from env with Render hostname, reject wildcard"`

---

### Task 3: Лимит публичных POST по реальному IP (п. 5)

**Files:**
- Modify: `back/api/throttles.py`, `back/api/views.py` (`ContactMessageView`, `ProductReviewViewSet`, `ProductQuestionViewSet`, `OrderViewSet`)
- Test: `back/api/test_spam.py` (создать, класс `PublicWriteThrottleTest`)

**Interfaces:**
- Produces в `api/throttles.py`:
  - `RealClientIPMixin` с `get_ident(self, request) -> str | None` — тело из текущего `LoginRateThrottle.get_ident` (переносится, `LoginRateThrottle` наследует миксин, поведение не меняется).
  - `PUBLIC_WRITE_RATE = "30/hour"`; `class PublicWriteThrottle(RealClientIPMixin, SimpleRateThrottle)`: `scope = "public_write"`, `rate = PUBLIC_WRITE_RATE`, `cache = caches["throttle"]`; `allow_request` возвращает `True` для `SAFE_METHODS`; ключ — `scope + ident` для любого пользователя.
  - `PUBLIC_WRITE_THROTTLES = [AnonRateThrottle, UserRateThrottle, PublicWriteThrottle]` — ставится в `throttle_classes` четырёх вьюх (сохраняет общие лимиты).

- [ ] **Step 1: Падающие тесты** (`setUp`: очистить все кэши; товар; `REMOTE_ADDR="10.0.0.1"`; хелпер `_contact(xff)` → POST `/api/contact/message/` `{"name":"A","email":"a@a.uz","message":"hi"}`):

```python
def test_31st_public_post_is_throttled(self):
    for _ in range(30):
        self.assertEqual(self._contact("203.0.113.7").status_code, 201)
    self.assertEqual(self._contact("203.0.113.7").status_code, 429)
def test_spoofed_xff_does_not_bypass(self):
    for i in range(30): self._contact(f"1.1.1.{i}, 203.0.113.7")
    self.assertEqual(self._contact("9.9.9.9, 203.0.113.7").status_code, 429)
def test_bucket_shared_across_endpoints(self):
    for _ in range(30): self._contact("203.0.113.7")
    r = self.api.post(f"/api/products/{self.product.slug}/reviews/",
                      {"author_name": "A", "rating": 5, "text": "ok"}, format="json",
                      REMOTE_ADDR="10.0.0.1", HTTP_X_FORWARDED_FOR="203.0.113.7")
    self.assertEqual(r.status_code, 429)
def test_reading_is_not_throttled(self):
    for _ in range(30): self._contact("203.0.113.7")
    r = self.api.get(f"/api/products/{self.product.slug}/reviews/", REMOTE_ADDR="10.0.0.1",
                     HTTP_X_FORWARDED_FOR="203.0.113.7")
    self.assertEqual(r.status_code, 200)
```

- [ ] **Step 2:** Run: `... test api.test_spam.PublicWriteThrottleTest` → FAIL (31-й запрос 201).
- [ ] **Step 3:** Реализовать Interfaces; подключить `PUBLIC_WRITE_THROTTLES` к четырём вьюхам.
- [ ] **Step 4:** Run класс → PASS; полная команда → OK (тесты `LoginThrottleTest` подтверждают, что перенос в миксин ничего не сломал; `test_orders` должен остаться зелёным — если упирается в лимит, очищать кэши в его `setUp`).
- [ ] **Step 5:** `git commit -am "fix(security): rate-limit public writes per real client IP"`

---

### Task 4: Модерация отзывов/вопросов, лимиты длины, 404 (п. 5)

**Files:**
- Modify: `back/api/serializers.py` (`ProductReviewSerializer`, `ProductQuestionSerializer`, `ContactMessageSerializer`, `OrderSerializer`), `back/api/views.py` (`perform_create` в `ProductReviewViewSet` / `ProductQuestionViewSet`)
- Modify: `Front/src/views/ProductDetailPage.vue` (`submitReview`, `submitQuestion`, textarea), `Front/src/components/ContactFormComponent.vue`, `Front/src/views/CartPage.vue` (textarea `maxlength`)
- Test: `back/api/test_spam.py` (класс `ModerationAndLimitsTest`)

**Interfaces:**
- Produces: константы длины из Global Constraints в `api/serializers.py` (через `extra_kwargs={"text": {"max_length": ...}}` и т.п., модели не меняются).
- Контракт API: POST отзыва/вопроса → 201, в ответе `is_published: false`; несуществующий slug → 404.

- [ ] **Step 1: Падающие тесты** (`setUp` очищает кэши; товар `slug="cam"`; staff). Хелперы (анонимный `self.api`, возвращают ответ): `_review(text, rating=5)` → POST `/api/products/cam/reviews/` `{"author_name": "A", "rating": rating, "text": text}`; `_question(text)` → `/api/products/cam/questions/`; `_contact(message)` → `/api/contact/message/` с `name`/`email`; `_order(comment)` → `/api/orders/` с одной позицией товара `cam` (формат `CartPage.vue`, как в `test_orders.py`):

```python
def test_new_review_hidden_until_moderated(self):
    r = self._review(text="ok")
    self.assertEqual((r.status_code, r.data["is_published"]), (201, False))
    self.assertEqual(self.api.get("/api/products/cam/reviews/").data["count"], 0)
def test_admin_publish_makes_review_visible(self):
    rid = self._review(text="ok").data["id"]
    self.api.force_authenticate(self.staff)
    self.assertEqual(self.api.patch(f"/api/admin/reviews/{rid}/", {"is_published": True}, format="json").status_code, 200)
    self.api.force_authenticate(None)
    self.assertEqual(self.api.get("/api/products/cam/reviews/").data["count"], 1)
def test_new_question_hidden_until_moderated(self): ...   # то же для /questions/
def test_text_length_limits(self):
    self.assertEqual(self._review(text="x" * 2000).status_code, 201)
    self.assertEqual(self._review(text="x" * 2001).status_code, 400)
    self.assertEqual(self._question(text="x" * 1001).status_code, 400)
    self.assertEqual(self._contact(message="x" * 3001).status_code, 400)
    self.assertEqual(self._order(comment="x" * 1001).status_code, 400)
def test_review_for_unknown_product_is_404(self):
    r = self.api.post("/api/products/nope/reviews/", {"author_name": "A", "rating": 5, "text": "t"}, format="json")
    self.assertEqual(r.status_code, 404)
```

- [ ] **Step 2:** Run класс → FAIL (`is_published` True, 2001 принимается, `DoesNotExist`).
- [ ] **Step 3:** Backend: `perform_create` → `product = get_object_or_404(Product, slug=...)`; `serializer.save(product=product, is_published=False)`; лимиты в сериализаторах.
- [ ] **Step 4:** Run класс → PASS; полная команда → OK.
- [ ] **Step 5:** Frontend: в `submitReview`/`submitQuestion` — если `res.data.is_published` то `unshift`, иначе показать под формой точный текст из Global Constraints (новые `ref<string>` `reviewNotice` / `questionNotice`); `maxlength` у textarea: отзыв 2000, вопрос 1000, контакты 3000, комментарий заказа 1000. Run: `npm run build` в `Front/` → успешно.
- [ ] **Step 6:** Ручная проверка (`npm run dev` + backend `DEBUG=True runserver`): оставить отзыв → видно сообщение о модерации, в списке отзыва нет; в админке «Отзывы» → «Опубликовать» → отзыв появился на странице товара.
- [ ] **Step 7:** `git commit -am "fix(security): moderate new reviews/questions, cap public text lengths"`

---

### Task 5: Проверка загружаемых изображений (п. 6)

**Files:**
- Create: `back/api/uploads.py`
- Modify: `back/api/views.py` (удалить `ALLOWED_IMAGE_TYPES`, `MAX_UPLOAD_SIZE`, старую `validate_uploaded_image`, импортировать новую; удалить action `ProductViewSet.upload_image`), `back/api/serializers.py` (`ImageAdminSerializer.validate_image`)
- Modify: `Front/src/api/index.ts` (удалить неиспользуемый `productsAPI.uploadImages`)
- Test: `back/api/test_uploads.py`

**Interfaces:**
- Produces в `api/uploads.py`: `ALLOWED_IMAGE_FORMATS = {"JPEG": "jpg", "PNG": "png", "GIF": "gif", "WEBP": "webp"}`, `MAX_UPLOAD_SIZE`, `MAX_IMAGE_PIXELS` (значения из Global Constraints), `validate_uploaded_image(file) -> tuple[bool, str | None]` — та же сигнатура, что у старой функции (4 вызова во вьюхах не меняются). Порядок: размер → `Image.open` (`DecompressionBombWarning` как ошибка) → `width*height > MAX_IMAGE_PIXELS` → `verify()` → формат из словаря. При успехе: `file.seek(0)`, `file.name = f"{uuid4().hex}.{ext}"`. Любое исключение Pillow → `(False, "<сообщение>")`.
- Хелпер тестов: `make_upload(fmt="PNG", size=(10, 10), name="a.png", content_type="image/png", mode="RGB") -> SimpleUploadedFile` (картинка генерируется Pillow в `BytesIO`).

- [ ] **Step 1: Падающие тесты** — модульные (`SimpleTestCase`):

```python
def test_real_png_accepted_and_renamed(self):
    f = make_upload(name="evil.html")
    self.assertEqual(validate_uploaded_image(f), (True, None))
    self.assertTrue(f.name.endswith(".png")); self.assertNotIn("evil", f.name)
def test_html_disguised_as_png_rejected(self):
    f = SimpleUploadedFile("x.png", b"<html><script>alert(1)</script></html>", content_type="image/png")
    self.assertFalse(validate_uploaded_image(f)[0])
def test_svg_rejected(self):
    f = SimpleUploadedFile("x.svg", b'<svg xmlns="http://www.w3.org/2000/svg"><script>alert(1)</script></svg>', content_type="image/svg+xml")
    self.assertFalse(validate_uploaded_image(f)[0])
def test_truncated_image_rejected(self):
    data = make_upload().read()[:60]
    self.assertFalse(validate_uploaded_image(SimpleUploadedFile("x.png", data, content_type="image/png"))[0])
def test_unsupported_format_rejected(self):
    self.assertFalse(validate_uploaded_image(make_upload(fmt="BMP", name="x.bmp", content_type="image/bmp"))[0])
def test_oversize_rejected(self):
    self.assertFalse(validate_uploaded_image(SimpleUploadedFile("x.png", b"0" * (MAX_UPLOAD_SIZE + 1)))[0])
def test_too_many_pixels_rejected(self):
    self.assertFalse(validate_uploaded_image(make_upload(size=(8000, 8000), mode="1"))[0])
def test_large_phone_photo_accepted(self):
    self.assertTrue(validate_uploaded_image(make_upload(fmt="JPEG", size=(4000, 3000), name="IMG_1.jpg", content_type="image/jpeg"))[0])
```

  Интеграционные (`TestCase`, staff, товар):

```python
def test_admin_upload_rejects_html(self): ...        # POST /api/admin/products/{id}/upload-image/ {"images": html-as-png} → 400, Image.objects.count() == 0
def test_admin_upload_accepts_png(self): ...          # → 201, Image.objects.get().image.name endswith ".png", startswith "products/"
def test_public_upload_route_removed(self): ...       # обычный пользователь, POST /api/products/{slug}/upload-image/ → 404
def test_image_admin_rejects_svg(self): ...           # POST /api/admin/images/ {"product": id, "image": svg} → 400
def test_image_admin_patch_order_still_works(self): ...  # Image с image="products/old.svg"; PATCH /api/admin/images/{id}/ {"order": 3} → 200, order == 3
```

- [ ] **Step 2:** Run: `... test api.test_uploads` → FAIL (`ModuleNotFoundError: api.uploads`). Затем создать пустой модуль с константами и заглушкой, вызывающей старую логику, — интеграционные тесты должны падать по сути (HTML принят, публичный маршрут отвечает), а не на импорте.
- [ ] **Step 3:** Реализовать `validate_uploaded_image`; подключить во `views.py` и в `ImageAdminSerializer.validate_image` (ошибка → `serializers.ValidationError`); удалить action `ProductViewSet.upload_image` и `productsAPI.uploadImages` во фронте.
- [ ] **Step 4:** Run `api.test_uploads` → PASS; полная команда → OK; `npm run build` → успешно.
- [ ] **Step 5:** `git commit -am "fix(security): validate uploaded images by content, drop SVG, remove public upload route"`

---

### Task 6: Токены — только staff, logout и смена пароля отзывают refresh (п. 6–7)

**Files:**
- Create: `back/api/auth.py`
- Modify: `back/api/views.py` (`AdminTokenObtainPairView.serializer_class`, `admin_logout`, `admin_change_password`)
- Modify: `Front/src/api/admin.ts` (`authAPI.logout` отправляет refresh; `authAPI.changePassword` сохраняет новые токены)
- Test: `back/api/test_auth.py`

**Interfaces:**
- Produces в `api/auth.py`:
  - `StaffTokenObtainPairSerializer(TokenObtainPairSerializer)` — после `super().validate()` при `not self.user.is_staff` → `AuthenticationFailed(self.error_messages["no_active_account"], "no_active_account")` (401, тот же ответ, что при неверном пароле — не раскрывать, что пользователь существует).
  - `revoke_all_refresh_tokens(user) -> int` — `BlacklistedToken.get_or_create` для каждого `OutstandingToken` пользователя; возвращает число отозванных.
- Контракт API:
  - `POST /api/admin/auth/logout/` — `AllowAny`, тело `{"refresh": "<token>"}`; нет поля → 400; валидный → blacklist, 200; невалидный/уже отозванный → 200 (токен и так не работает).
  - `POST /api/admin/auth/change-password/` — при успехе отзывает все refresh пользователя и возвращает `{"message": ..., "access": ..., "refresh": ...}` (новая пара для текущей сессии).

- [ ] **Step 1: Падающие тесты** (`setUp` очищает все кэши; staff `admin`/`Str0ng-pass-123`; обычный `user`/`Str0ng-pass-123`). Хелперы на свежем `APIClient()`: `_login(username)` → POST `/api/admin/auth/login/` с паролем `Str0ng-pass-123`; `_refresh(token)` → POST `/api/admin/auth/refresh/` `{"refresh": token}`; `_change_password(access, old, new)` → POST `/api/admin/auth/change-password/` `{"old_password": old, "new_password": new}` с `Authorization: Bearer <access>`:

```python
def test_non_staff_cannot_get_tokens(self):
    self.assertEqual(self._login("user").status_code, 401)
def test_staff_gets_tokens(self):
    self.assertIn("refresh", self._login("admin").data)
def test_logout_revokes_refresh(self):
    t = self._login("admin").data
    self.api.credentials(HTTP_AUTHORIZATION=f"Bearer {t['access']}")
    self.assertEqual(self.api.post("/api/admin/auth/logout/", {"refresh": t["refresh"]}, format="json").status_code, 200)
    self.assertEqual(self._refresh(t["refresh"]).status_code, 401)
def test_logout_without_access_token_still_revokes(self):
    t = self._login("admin").data
    self.assertEqual(APIClient().post("/api/admin/auth/logout/", {"refresh": t["refresh"]}, format="json").status_code, 200)
    self.assertEqual(self._refresh(t["refresh"]).status_code, 401)
def test_logout_requires_refresh_field(self):
    self.assertEqual(APIClient().post("/api/admin/auth/logout/", {}, format="json").status_code, 400)
def test_change_password_revokes_other_sessions(self):
    old = self._login("admin").data
    current = self._login("admin").data
    self._change_password(current["access"], "Str0ng-pass-123", "N3w-strong-pass-456")
    self.assertEqual(self._refresh(old["refresh"]).status_code, 401)
def test_change_password_returns_working_new_tokens(self):
    t = self._login("admin").data
    r = self._change_password(t["access"], "Str0ng-pass-123", "N3w-strong-pass-456")
    self.assertEqual(r.status_code, 200)
    self.assertEqual(self._refresh(r.data["refresh"]).status_code, 200)
```

- [ ] **Step 2:** Run: `... test api.test_auth` → FAIL (не-staff получает 200, refresh после logout работает).
- [ ] **Step 3:** Реализовать `api/auth.py` и изменения вьюх по контракту (новая пара — `RefreshToken.for_user(user)` после отзыва старых).
- [ ] **Step 4:** Run `api.test_auth` → PASS; полная команда → OK (лимит логина 5/час: тесты должны очищать кэш `throttle` в `setUp`).
- [ ] **Step 5:** Frontend: `authAPI.logout` → `adminApi.post("/admin/auth/logout/", { refresh: tokenStorage.getRefreshToken() })` (в `finally` по-прежнему `clearTokens()`); `authAPI.changePassword` → если в ответе есть `access`, вызвать `tokenStorage.setTokens(data.access, data.refresh)`. Run: `npm run build` → успешно.
- [ ] **Step 6:** Ручная проверка: войти в админку → «Выйти» → в DevTools повторить запрос `/admin/auth/refresh/` со старым refresh → 401; сменить пароль → админка продолжает работать, вход в другом браузере со старой сессией слетает максимум через 15 минут.
- [ ] **Step 7:** `git commit -am "fix(security): staff-only tokens, logout and password change revoke refresh tokens"`

---

### Task 7: Ограничение тяжёлых фильтров и мусорных параметров (п. 8)

**Files:**
- Modify: `back/api/views.py` (`apply_product_filters`, `products_by_feature_value`, `get_queryset` в `CategoryViewSet` и `NewsViewSet`)
- Test: `back/api/test_dos.py`

**Interfaces:**
- Produces: `MAX_FEATURE_FILTERS`, `MAX_BY_FEATURE_RESULTS`, `MAX_LIST_LIMIT` в `api/views.py` (значения из Global Constraints); хелпер `parse_limit(raw: str | None) -> int | None` — не число или `< 1` → `None` (без среза), иначе `min(value, MAX_LIST_LIMIT)`.
- Поведение: из параметров `feature_<id>` учитываются первые `MAX_FEATURE_FILTERS` с целыми `id` и `value`, остальные игнорируются; блок `taggroup_*` удаляется (поле не существует, фронт его не шлёт); `/products/by-feature/` по-прежнему отдаёт массив (не пагинацию — контракт фронта), но не длиннее `MAX_BY_FEATURE_RESULTS`.

- [ ] **Step 1: Падающие тесты:**

```python
def test_feature_filters_capped(self):
    params = {f"feature_{i}": "1" for i in range(1, 51)}
    request = Request(APIRequestFactory().get("/api/products/", params))
    sql = str(apply_product_filters(request, Product.objects.all()).query)
    self.assertLessEqual(sql.count('"api_productfeature"'), MAX_FEATURE_FILTERS)
def test_non_integer_feature_value_ignored(self):
    self.assertEqual(self.client.get("/api/products/", {"feature_1": "abc"}).status_code, 200)
def test_taggroup_param_does_not_crash(self):
    self.assertEqual(self.client.get("/api/products/", {"taggroup_color": "red"}).status_code, 200)
def test_negative_limit_does_not_crash(self):
    for url in ("/api/categories/", "/api/news/"):
        self.assertEqual(self.client.get(url, {"limit": "-1"}).status_code, 200)
def test_by_feature_results_capped(self):
    # 105 товаров с одним FeatureValue "4K"
    r = self.client.get("/api/products/by-feature/", {"value": "4K"})
    self.assertEqual((r.status_code, len(r.data)), (200, MAX_BY_FEATURE_RESULTS))
```

- [ ] **Step 2:** Run: `... test api.test_dos` → FAIL (50 JOIN, `FieldError`, `AssertionError: Negative indexing`, 105 результатов).
- [ ] **Step 3:** Реализовать по Interfaces.
- [ ] **Step 4:** Run `api.test_dos` → PASS; полная команда → OK (существующие тесты фильтров тегов/категорий/брендов — регрессия).
- [ ] **Step 5:** `git commit -am "fix(security): cap feature filters and result sizes, ignore malformed params"`

---

### Task 8: Безопасные ссылки баннеров (п. 9)

**Files:**
- Create: `back/api/validators.py`
- Modify: `back/api/serializers.py` (`BannerSerializer.validate_link`)
- Test: `back/api/test_validators.py`

**Interfaces:**
- Produces: `SAFE_LINK_SCHEMES = {"", "http", "https", "mailto", "tel"}`; `validate_safe_link(value: str | None) -> str | None` — `None`/`""` возвращаются как есть; иначе `strip()`, для проверки удаляются все пробельные и управляющие символы (браузеры их игнорируют в схеме), `urlsplit(cleaned).scheme.lower()` не в `SAFE_LINK_SCHEMES` → `serializers.ValidationError`; возвращается `strip()`-нутое исходное значение.

- [ ] **Step 1: Падающие тесты:**

```python
def test_dangerous_links_rejected(self):
    for link in ("javascript:alert(1)", " JaVaScRiPt:alert(1)", "java\tscript:alert(1)",
                 "data:text/html,<script>alert(1)</script>", "vbscript:msgbox(1)"):
        with self.subTest(link=link), self.assertRaises(ValidationError):
            validate_safe_link(link)
def test_safe_links_allowed(self):
    for link in ("catalog/cameras", "/brands", "#promo", "https://ncf.uz/a?b=1", "http://x.uz", "tel:+998901234567", "", None):
        with self.subTest(link=link):
            self.assertEqual(validate_safe_link(link), link.strip() if link else link)
def test_admin_banner_api_rejects_javascript(self):
    # staff PATCH /api/admin/banners/{id}/ {"link": "javascript:alert(1)"} → 400, link в БД не изменился
```

- [ ] **Step 2:** Run: `... test api.test_validators` → FAIL (`ModuleNotFoundError: api.validators`).
- [ ] **Step 3:** Реализовать; подключить в `BannerSerializer.validate_link`.
- [ ] **Step 4:** Run `api.test_validators` → PASS; полная команда → OK.
- [ ] **Step 5:** `git commit -am "fix(security): allow only safe URL schemes in banner links"`

---

### Task 9: Деплой и проверка на проде (вручную, владелец)

- [ ] **Step 1:** На Render проверить версию Python (Settings → Environment / `PYTHON_VERSION`): нужна ≥ 3.10 (Django 5.2, Pillow 12). Если ниже — выставить `PYTHON_VERSION=3.11.9` до деплоя.
- [ ] **Step 2:** Деплой ветки (после п. 1–4). В логах сборки — установка `Django-5.2.17`, без ошибок `pip`.
- [ ] **Step 3: Смоук:**
  - Отзыв с сайта → сообщение о модерации; в админке «Отзывы» — «Скрыт»; «Опубликовать» → появился на сайте.
  - Загрузка JPG товара в админке → картинка видна; загрузка `.svg` или переименованного `.html` → ошибка.
  - «Выйти» из админки → повторный вход нужен; смена пароля → админка работает дальше.
  - `/api/products/?taggroup_x=1` и `/api/categories/?limit=-1` → 200, не 500.
  - Баннер со ссылкой `javascript:alert(1)` не сохраняется.
- [ ] **Step 4:** В админке «Отзывы» и «Вопросы» просмотреть уже опубликованные записи за время работы без модерации и скрыть спам.
