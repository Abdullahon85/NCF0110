# NCF — каталог товаров с админ-панелью

Интернет-каталог (камеры, системы безопасности и т.п.) с заявками на покупку, отзывами, вопросами о товарах, новостями и собственной админ-панелью.

| Часть | Стек | Папка |
|---|---|---|
| Бэкенд (REST API) | Python 3.10+, Django 5.2, Django REST Framework, SimpleJWT | `back/` |
| Фронтенд (сайт + админка) | Vue 3, TypeScript, Vite, Pinia, Node 22 LTS | `Front/` |
| База данных | SQLite (один файл, отдельный сервер БД не нужен) | — |
| Развёртывание | Один Docker-контейнер (`Dockerfile`, `docker-compose.yml`) или вручную | корень |

Проект не привязан к хостингу: все домены, ключи и адреса задаются переменными окружения.

---

## Быстрый старт (локально)

### Бэкенд

```bash
cd back
python -m venv .venv
# Windows: .venv\Scripts\activate   |   Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt

# Linux/macOS:
export DEBUG=True
# Windows PowerShell:
# $env:DEBUG="True"

python manage.py migrate
python manage.py createsuperuser      # вход в админ-панель сайта
python manage.py runserver            # http://127.0.0.1:8000
```

`DEBUG=True` обязателен для локального запуска: без него Django считает окружение production-окружением и требует `SECRET_KEY` и `ALLOWED_HOSTS`. База — SQLite (`back/db.sqlite3`), а ключ генерируется случайно при каждом запуске.

### Фронтенд

```bash
cd Front
npm ci          # строго по package-lock.json
npm run dev     # http://localhost:5173
```

Dev-сервер Vite проксирует `/api` и `/media` на `http://127.0.0.1:8000`, поэтому бэкенд должен быть запущен.

- Сайт: http://localhost:5173
- Админ-панель: http://localhost:5173/admin/login. Вход только для пользователей с `is_staff` (суперпользователь подходит).

---

## Переменные окружения бэкенда

Полный шаблон с комментариями: [`back/.env.example`](back/.env.example). Django **не читает** `.env` сам. Переменные задаются в окружении процесса: systemd `Environment=`, `docker run -e`, панель хостинга и т.п.

| Переменная | Обязательна в production | Описание |
|---|---|---|
| `SECRET_KEY` | да | Минимум 50 символов. Генерация: `python -c "import secrets; print(secrets.token_urlsafe(50))"` (только буквы, цифры, `-` и `_`: в `.env` символы `$` и `#` портят значение). |
| `DEBUG` | — | `True` только локально. По умолчанию `False`. |
| `ALLOWED_HOSTS` | да | Домены API через запятую, например `api.shop.uz`. `*` запрещён. |
| `CORS_ALLOWED_ORIGINS` | если фронт на другом домене | Например `https://shop.uz`, без пути. Если фронт и API на одном домене, оставить пустым. |
| `SQLITE_PATH` | — | Путь к файлу базы SQLite. Пусто = `back/db.sqlite3`. В Docker задан в образе: `/data/db.sqlite3`. `DATABASE_URL` больше не используется: если он задан, приложение не запустится (чтобы старый `.env` с PostgreSQL не подключился молча к другой базе). |
| `MEDIA_ROOT` | — | Папка загруженных картинок. Пусто = `back/media`. В Docker: `/data/media`. |
| `TRUSTED_PROXY_COUNT` | — | Сколько прокси перед Django дописывают `X-Forwarded-For`: nginx → gunicorn = `1`, без прокси = `0`. Нужна для лимитов по реальному IP, см. «Безопасность». |
| `SECURE_SSL_REDIRECT` | — | `True` по умолчанию. `False`, если HTTPS-редирект делает nginx или балансировщик. |
| `SERVE_MEDIA` | — | `True` (по умолчанию): Django сам отдаёт `/media/`. `False`, если `/media/` раздаёт nginx (рекомендуется). |
| `MEDIA_URL` | если API на другом домене | Пусто = `/media/`. При API на отдельном домене: `https://api.shop.uz/media/`, тогда адреса картинок в ответах API будут полными. |
| `CACHE_DIR` | — | Каталог файлового кэша для лимитов запросов. По умолчанию системный temp. |
| `ENABLE_DJANGO_ADMIN` | — | Стандартная Django-админка `/dashboard-ctrl-panel/`. По умолчанию выключена в production. |

### Фронтенд

[`Front/.env.example`](Front/.env.example): `VITE_API_URL` задаётся **на этапе сборки** (`npm run build`). Пусто или не задано означает `/api` на том же домене (рекомендуется).

### Фронт и API на разных доменах

Например, `shop.uz` для сайта и `api.shop.uz` для API. Нужны все три настройки:

1. При сборке фронта: `VITE_API_URL=https://api.shop.uz/api`.
2. На бэкенде: `CORS_ALLOWED_ORIGINS=https://shop.uz`.
3. На бэкенде: `MEDIA_URL=https://api.shop.uz/media/`. Без этого картинки будут запрашиваться с домена сайта и не загрузятся.

---

## Docker (рекомендуемый способ)

Всё работает в **одном контейнере** (`Dockerfile` в корне, сервис `ncf` в `docker-compose.yml`):

- при сборке Vue-сайт собирается (`npm run build`) и кладётся в образ рядом с Django;
- gunicorn + Django отдают на одном порту всё: сайт и админ-панель (`/`), REST API (`/api/`), загруженные картинки (`/media/`), статику Django-админки (`/static/`);
- база — **SQLite**, файл `/data/db.sqlite3`; картинки — `/data/media`. Папка `/data` — это том `ncf-data`, он переживает пересборку и перезапуск контейнера;
- при старте контейнер один раз применяет миграции и запускает gunicorn. Ждать базу не нужно: это файл на томе.

**Внешние сервисы не нужны:** ни PostgreSQL, ни nginx внутри, ни почты, ни Redis, ни S3, ни очередей. Нужен только постоянный том `ncf-data`.

```bash
cp .env.docker.example .env        # заполнить SECRET_KEY и ALLOWED_HOSTS
docker compose up -d --build
docker compose exec ncf python manage.py createsuperuser
docker compose logs -f ncf         # проверить, что миграции прошли и gunicorn запущен
```

Сайт откроется на порту `HTTP_PORT` (по умолчанию 8080). Если открываете его по IP сервера (`http://IP:8080`), добавьте этот IP в `ALLOWED_HOSTS`, иначе любая страница ответит `400 Bad Request`. HTTPS и домен настраиваются на обратном прокси сервера (nginx, traefik и т.п.), который проксирует домен на этот порт. HTTPS-редирект делает этот прокси, поэтому в шаблоне `SECURE_SSL_REDIRECT=False`.

> **Том `ncf-data` — это вся база и все картинки.** Не удаляйте его: `docker compose down -v` и `docker volume rm` стирают данные безвозвратно. Обычные `docker compose down`, `up --build`, `pull` данные не трогают.

### Через реестр образов (сборка на одной машине, запуск на сервере)

1. **На машине сборки** (нужен Docker; на Windows — Docker Desktop), из корня репозитория:
   - Windows: `.\deploy\push-images.ps1 -Registry registry.example.uz:5000`
   - Linux/macOS: `./deploy/push-images.sh registry.example.uz:5000`

   Скрипт спросит логин и пароль реестра, соберёт один образ `ncf` и запушит его с тегами `<коммит>` и `latest`. Если push падает с ошибкой `http: server gave HTTP response to HTTPS client`, реестр работает по HTTP: добавьте его в `insecure-registries` (Docker Desktop → Settings → Docker Engine) и повторите.
2. **На сервере** нужны только `docker-compose.yml` и `.env`. В `.env` указать `REGISTRY`, `HTTP_PORT` и остальные переменные, затем:
   ```bash
   docker login registry.example.uz:5000
   docker compose pull && docker compose up -d
   docker compose exec ncf python manage.py createsuperuser
   ```
   Домен проксируется на `HTTP_PORT`: туда идут сайт, админка, `/api` и `/media`.

- **`TRUSTED_PROXY_COUNT`:** `1`, если перед контейнером стоит обратный прокси сервера, который дописывает `X-Forwarded-For` (обычный вариант с HTTPS); `0`, если порт контейнера открыт в интернет напрямую. Проверка после запуска: 6 неверных попыток входа подряд, каждая с новым заголовком `X-Forwarded-For`, на шестой должны дать `429`. Если `429` приходит всем пользователям сразу, значение слишком маленькое.
- **Резервные копии базы:** `docker compose exec ncf python manage.py backup_db --keep 14` — согласованная копия в `/data/backups/` (на том же томе), можно запускать на работающем сайте, например из cron раз в сутки. Не копируйте `db.sqlite3` простым `cp` во время работы: из-за WAL-журнала копия может оказаться неполной. Чтобы забрать копии и картинки с сервера: `docker run --rm -v <проект>_ncf-data:/d -v $PWD:/b alpine tar czf /b/ncf-data.tgz -C /d backups media`.
- **Перенос существующей базы:** остановить контейнер (`docker compose stop ncf`), скопировать файл в том (`docker compose cp ./db.sqlite3 ncf:/data/db.sqlite3`), запустить (`docker compose start ncf`); недостающие миграции применятся сами.
- **Свой каталог вместо тома:** вместо `ncf-data:/data` можно указать папку сервера, например `/srv/ncf-data:/data`. Владельцем папки должен быть пользователь с UID 1000 (`chown -R 1000:1000 /srv/ncf-data`), иначе контейнер не сможет писать базу.
- **Обновление:** `git pull && docker compose up -d --build`. Миграции применятся при старте контейнера.
- **Очистка токенов:** раз в сутки `docker compose exec ncf python manage.py flushexpiredtokens`.
- **Нагрузка:** SQLite в режиме WAL спокойно обслуживает каталог с админкой (много чтений, редкие записи). Запуск нескольких копий контейнера на разных серверах с одной базой не поддерживается.

## Production без Docker (пример: Linux + nginx + gunicorn)

Подойдёт любой хостинг. Ниже минимальный вариант на одном сервере, где фронт и API работают на одном домене.

### 1. Бэкенд

```bash
cd back
python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt

export SECRET_KEY='...' ALLOWED_HOSTS='shop.uz' SQLITE_PATH=/srv/ncf/data/db.sqlite3 \
       TRUSTED_PROXY_COUNT=1 SECURE_SSL_REDIRECT=False SERVE_MEDIA=False

python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
python manage.py check --deploy          # допустимо только W008, если HTTPS-редирект делает nginx

gunicorn config.wsgi:application --bind 127.0.0.1:8000 --workers 3
```

Для постоянной работы gunicorn запускается как systemd-сервис, например `/etc/systemd/system/ncf.service`:

```ini
[Unit]
Description=NCF Django API
After=network.target

[Service]
User=www-data
WorkingDirectory=/srv/ncf/back
EnvironmentFile=/srv/ncf/back/.env          # KEY=value построчно, по образцу back/.env.example
ExecStart=/srv/ncf/back/.venv/bin/gunicorn config.wsgi:application --bind 127.0.0.1:8000 --workers 3
Restart=always

[Install]
WantedBy=multi-user.target
```

Затем: `systemctl daemon-reload && systemctl enable --now ncf`. У пользователя сервиса должны быть права на запись в `back/media/`.

### 2. Фронтенд

```bash
cd Front
npm ci
npm run build          # результат в Front/dist
```

### 3. nginx

```nginx
server {
    listen 443 ssl;
    http2 on;                            # nginx >= 1.25.1; на старых: listen 443 ssl http2;
    server_name shop.uz;
    # ssl_certificate ...; ssl_certificate_key ...;

    client_max_body_size 12m;            # загрузка картинок до 10 МБ

    root /srv/ncf/Front/dist;
    index index.html;

    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $remote_addr;   # перезаписать, а не дописать к клиентскому
        proxy_set_header X-Forwarded-Proto https;
    }

    location /media/ {
        alias /srv/ncf/back/media/;
        add_header X-Content-Type-Options nosniff;
    }

    location /static/ {                  # статика Django (нужна только для Django-админки)
        alias /srv/ncf/back/staticfiles/;
    }

    # Только если включена стандартная Django-админка (ENABLE_DJANGO_ADMIN=True):
    # location /dashboard-ctrl-panel/ { proxy_pass http://127.0.0.1:8000; proxy_set_header Host $host;
    #     proxy_set_header X-Forwarded-For $remote_addr; proxy_set_header X-Forwarded-Proto https; }

    location / {
        try_files $uri $uri/ /index.html;   # SPA: все маршруты Vue отдают index.html
    }
}

server {
    listen 80;
    server_name shop.uz;
    return 301 https://$host$request_uri;
}
```

> ⚠️ **`TRUSTED_PROXY_COUNT` должен точно соответствовать схеме**, иначе лимиты запросов не работают:
> - nginx перед gunicorn и пишет `X-Forwarded-For $remote_addr` (как в примере) → `1`;
> - перед nginx есть ещё балансировщик или CDN → `1` + число этих прокси;
> - gunicorn доступен из интернета напрямую, без прокси → **`0`**. Если оставить `1`, атакующий подставит любой `X-Forwarded-For` и обойдёт лимит перебора паролей.
>
> Проверка после деплоя: 6 неверных попыток входа подряд, каждая с новым заголовком `X-Forwarded-For`, должны дать на шестой ответ `429`.

У пользователя nginx должны быть права на чтение `back/media/` и `Front/dist/`.

> HSTS: в production сайт отдаёт `Strict-Transport-Security` на 1 год с `includeSubDomains` и `preload`. Браузеры после этого заходят на домен и все его поддомены только по HTTPS. Включайте production-режим, когда HTTPS настроен на всех поддоменах; иначе уменьшите `SECURE_HSTS_SECONDS` в `config/settings.py`.

### 4. Обслуживание

- **Резервные копии:** база данных (`python manage.py backup_db --keep 14` по расписанию) и `back/media/` (картинки товаров, брендов, категорий и баннеров; в git их нет).
- **Очистка таблиц токенов:** раз в сутки, например через cron:

  ```bash
  cd /srv/ncf/back && .venv/bin/python manage.py flushexpiredtokens
  ```

### 5. Обновление (повторный деплой)

```bash
cd /srv/ncf && git pull
cd back && .venv/bin/pip install -r requirements.txt
.venv/bin/python manage.py migrate && .venv/bin/python manage.py collectstatic --noinput
sudo systemctl restart ncf
cd ../Front && npm ci && npm run build
```

После первого деплоя этой версии все администраторы должны войти заново: старые токены недействительны.
---

## Тесты и проверки

```bash
cd back
DEBUG=True python manage.py test api config
DEBUG=True python manage.py makemigrations --check --dry-run
pip-audit -r requirements.txt                      # (pip install pip-audit)

cd ../Front
npm run build                                      # включает проверку типов vue-tsc
npm test                                           # тесты утилит (node --test, нужен Node 22.18+)
npm audit --omit=dev                               # зависимости, попадающие в сайт
```

Тесты идут на SQLite (база в памяти). Кэш в тестах всегда в памяти (`config/test_runner.py`).

### Демо-раздел (посмотреть фильтры и страницу товара)

```bash
python manage.py demo_catalog            # раздел «Видеонаблюдение (демо)»: 15 товаров, характеристики, скидки, документы
python manage.py demo_catalog --remove   # удалить всё демо (у демо-данных slug начинается с demo-)
# в Docker: docker compose exec ncf python manage.py demo_catalog
```

### Стиль кода

```bash
cd back
pip install -r requirements-dev.txt
ruff format .        # оформление (настройки в back/pyproject.toml)
ruff check .         # ошибки и порядок импортов; ruff check --fix . исправит часть сам

cd ../Front
npm run format       # Prettier (.prettierrc.json); проверка без правок: npm run format:check
npm run lint         # ESLint (eslint.config.js): JS, TypeScript, Vue
```

Переводы строк файлов сохраняются как есть (Prettier `endOfLine: auto`, Ruff `line-ending = "auto"`).

---

## Структура

```
back/
  config/            settings.py, urls.py, env.py (чтение переменных окружения), views.py (отдача Vue-сайта в Docker), test_runner.py
  api/
    models.py        товары, категории, бренды, теги, характеристики, заказы, отзывы, вопросы, баннеры
    views.py         публичный API + админский API (/api/admin/...)
    serializers.py
    throttles.py     лимиты запросов по реальному IP
    uploads.py       проверка загружаемых изображений
    validators.py    проверка ссылок баннеров
    auth.py          JWT: только staff, отзыв refresh-токенов
    admin.py         стандартная Django-админка (по умолчанию выключена)
    test_*.py        тесты
Front/
  src/api/           index.ts (публичный API), admin.ts (админ API, JWT)
  src/views/         страницы сайта и админ-панели
docs/superpowers/    аудит безопасности и планы исправлений (история изменений)
```

---

## Безопасность (что уже сделано)

Подробно: `docs/superpowers/` (история аудита; шаги про Render/Netlify там устарели).

- **Без собственного `SECRET_KEY`, при `DEBUG` по умолчанию и без `ALLOWED_HOSTS` production не запустится.** Ключи, когда-либо попадавшие в репозиторий, отклоняются всегда.
- **JWT только для staff:** при входе и при каждом обновлении токена. Refresh-токены ротируются. «Выйти» отзывает refresh-токен. Смена пароля отзывает все сессии и все ранее выданные access-токены.
- **Лимиты по реальному IP:** вход 5 в час; отзывы, вопросы и сообщения вместе 30 в час; заказы 20 в час. Подмена `X-Forwarded-For` не обходит лимиты, если `TRUSTED_PROXY_COUNT` задан верно.
- **Заказы:** цена, название и артикул берутся из каталога на сервере, а не от клиента. Не больше 50 позиций, количество от 1 до 999.
- **Отзывы и вопросы** появляются на сайте только после публикации в админ-панели. Длина текстов ограничена.
- **Загрузка картинок:** проверка по содержимому (JPEG, PNG, GIF, WebP; до 10 МБ и 60 Мп), случайные имена файлов, SVG и HTML запрещены. Загружать может только staff.
- **CSV-экспорт заказов** экранирует формулы Excel.
- **Ссылки баннеров:** только `http(s)`, `mailto`, `tel`, `tg`, `viber` или относительные.
- **Зависимости:** `pip-audit` чистый; `npm audit --omit=dev` чистый. Остаётся уязвимость dev-сервера Vite/esbuild (`npm run dev`). На собранный сайт она не влияет, исправляется обновлением Vite до новой мажорной версии.

### Известные ограничения

- Тексты «О нас», новостей, брендов и описаний товаров — обычный текст из полей админки: при выводе HTML экранируется (`Front/src/utils/richText.ts`), сохраняются только переносы строк. HTML-разметка, введённая в эти поля, показывается как текст и не выполняется.
- Медиафайлы (`/data/media` в Docker) удаляются с диска вместе с записью или при замене картинки (`back/api/signals.py`).
- Медиафайлы хранятся на локальном диске (`back/media/`, в Docker — том `ncf-data`). При нескольких серверах нужно общее хранилище (S3 и т.п.).
- Стандартная Django-админка не ограничивает число попыток входа, поэтому в production она выключена (`ENABLE_DJANGO_ADMIN=False`).
