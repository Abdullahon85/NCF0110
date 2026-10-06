# NCF — каталог товаров с админ-панелью

Интернет-каталог (камеры, системы безопасности и т.п.) с заявками на покупку, отзывами, вопросами о товарах, новостями и собственной админ-панелью.

| Часть | Стек | Папка |
|---|---|---|
| Бэкенд (REST API) | Python 3.10+, Django 5.2, Django REST Framework, SimpleJWT | `back/` |
| Фронтенд (сайт + админка) | Vue 3, TypeScript, Vite, Pinia, Node 20 | `Front/` |
| База данных | PostgreSQL (production) или SQLite (локально). MSSQL не поддерживается. | — |
| Развёртывание | Docker Compose (`docker-compose.yml`) или вручную | корень |

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

`DEBUG=True` обязателен для локального запуска: без него Django считает окружение production-окружением и требует `SECRET_KEY` и `ALLOWED_HOSTS`. В режиме DEBUG без `DATABASE_URL` используется SQLite (`back/db.sqlite3`), а ключ генерируется случайно при каждом запуске.

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
| `DATABASE_URL` | рекомендуется | `postgres://user:password@host:5432/dbname` (опционально `?sslmode=require`). Пусто = SQLite. Спецсимволы в пароле кодируются: `@` → `%40`, `:` → `%3A`, `/` → `%2F`. |
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

В репозитории есть готовые образы и `docker-compose.yml`:

| Сервис | Образ | Что делает |
|---|---|---|
| `backend` | `back/Dockerfile` (Python 3.12, gunicorn) | REST API. При старте ждёт базу и применяет миграции. |
| `frontend` | `Front/Dockerfile` (сборка Vite → nginx 1.27) | Отдаёт сайт и админ-панель, проксирует `/api` на `backend`, раздаёт загруженные картинки из тома `media`. |
| `db` (опционально) | `postgres:16-alpine` | Только для тестового стенда: `--profile with-db`. В production используется PostgreSQL сервера. |

**Внешние сервисы не нужны:** ни почты, ни Redis, ни S3, ни очередей, ни внешних API. Нужны только PostgreSQL и постоянный том для картинок. **MSSQL не поддерживается** (используйте PostgreSQL).

```bash
cp .env.docker.example .env        # заполнить SECRET_KEY, ALLOWED_HOSTS, DATABASE_URL
docker compose up -d --build
docker compose exec backend python manage.py createsuperuser
docker compose logs -f backend     # проверить, что миграции прошли и gunicorn запущен
```

Сайт откроется на порту `HTTP_PORT` (по умолчанию 8080). HTTPS и домен настраиваются на обратном прокси сервера (nginx, traefik и т.п.), который проксирует домен на этот порт. HTTPS-редирект делает этот прокси, поэтому в шаблоне `SECURE_SSL_REDIRECT=False`.

### Через реестр образов (сборка на одной машине, запуск на сервере)

1. **На машине сборки** (нужен Docker; на Windows — Docker Desktop), из корня репозитория:
   - Windows: `.\deploy\push-images.ps1 -Registry registry.example.uz:5000`
   - Linux/macOS: `./deploy/push-images.sh registry.example.uz:5000`

   Скрипт спросит логин и пароль реестра, соберёт `ncf-backend` и `ncf-frontend` и запушит их с тегами `<коммит>` и `latest`. Если push падает с ошибкой `http: server gave HTTP response to HTTPS client`, реестр работает по HTTP: добавьте его в `insecure-registries` (Docker Desktop → Settings → Docker Engine) и повторите.
2. **На сервере** нужны только `docker-compose.yml` и `.env`. В `.env` указать `REGISTRY`, порты `HTTP_PORT` и `API_PORT` и остальные переменные, затем:
   ```bash
   docker login registry.example.uz:5000
   docker compose pull backend frontend && docker compose up -d
   docker compose exec backend python manage.py createsuperuser
   ```
   Домен проксируется на `HTTP_PORT`: туда идут сайт, админка, `/api` и `/media`. `API_PORT` — прямой доступ к API, для работы сайта он не нужен.

- **База на том же сервере, вне Docker:** `DATABASE_URL=postgres://ncf:ПАРОЛЬ@host.docker.internal:5432/ncf`. PostgreSQL должен принимать подключения из сети Docker: `listen_addresses` и правило в `pg_hba.conf` для подсети Docker, например `172.16.0.0/12`. База и пользователь создаются заранее: `CREATE USER ncf WITH PASSWORD '...'; CREATE DATABASE ncf OWNER ncf;`.
- **`TRUSTED_PROXY_COUNT`:** `1`, если порт контейнера `frontend` открыт напрямую; `2`, если перед ним обратный прокси сервера, который дописывает `X-Forwarded-For`. Проверка после запуска: 6 неверных попыток входа подряд, каждая с новым заголовком `X-Forwarded-For`, на шестой должны дать `429`. Если `429` приходит всем пользователям сразу, значение слишком маленькое.
- **Резервные копии:** база данных и том `media` (`docker run --rm -v <проект>_media:/m -v $PWD:/b alpine tar czf /b/media.tgz -C /m .`).
- **Обновление:** `git pull && docker compose up -d --build`. Миграции применятся при старте `backend`.
- **Очистка токенов:** раз в сутки `docker compose exec backend python manage.py flushexpiredtokens`.

## Production без Docker (пример: Linux + nginx + gunicorn)

Подойдёт любой хостинг. Ниже минимальный вариант на одном сервере, где фронт и API работают на одном домене.

### 1. Бэкенд

```bash
cd back
python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt

export SECRET_KEY='...' ALLOWED_HOSTS='shop.uz' DATABASE_URL='postgres://ncf:***@127.0.0.1:5432/ncf' \
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

- **Резервные копии:** база данных (`pg_dump` по расписанию) и `back/media/` (картинки товаров, брендов, категорий и баннеров; в git их нет).
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
npm audit --omit=dev                               # зависимости, попадающие в сайт
```

Тесты проходят на SQLite и на PostgreSQL 16: для этого задайте `DATABASE_URL`. Кэш в тестах всегда в памяти (`config/test_runner.py`).

---

## Структура

```
back/
  config/            settings.py, urls.py, env.py (чтение переменных окружения), test_runner.py
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

- Тексты «О нас», новостей, брендов и описаний товаров выводятся через `v-html`, то есть HTML из админки исполняется на сайте. Вводить их может только staff. Если админов будет несколько или контент будет приходить из внешних источников, стоит добавить санитизацию (например, DOMPurify).
- Медиафайлы хранятся на локальном диске (`back/media/`). При нескольких серверах нужно общее хранилище (S3 и т.п.).
- Стандартная Django-админка не ограничивает число попыток входа, поэтому в production она выключена (`ENABLE_DJANGO_ADMIN=False`).
