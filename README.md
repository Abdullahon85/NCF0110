# NCF — каталог товаров с админ-панелью

Интернет-каталог (камеры, системы безопасности и т.п.) с заявками на покупку, отзывами, вопросами о товарах, новостями и собственной админ-панелью.

| Часть | Стек | Папка |
|---|---|---|
| Бэкенд (REST API) | Python 3.10+, Django 5.2, Django REST Framework, SimpleJWT | `back/` |
| Фронтенд (сайт + админка) | Vue 3, TypeScript, Vite, Pinia, Node 20 | `Front/` |
| База данных | PostgreSQL (production) или SQLite (локально) | — |

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
| `SECRET_KEY` | да | Минимум 50 символов. Генерация: `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"` |
| `DEBUG` | — | `True` только локально. По умолчанию `False`. |
| `ALLOWED_HOSTS` | да | Домены API через запятую, например `api.shop.uz`. `*` запрещён. |
| `CORS_ALLOWED_ORIGINS` | если фронт на другом домене | Например `https://shop.uz`, без пути. Если фронт и API на одном домене, оставить пустым. |
| `DATABASE_URL` | рекомендуется | `postgres://user:password@host:5432/dbname` (опционально `?sslmode=require`). Пусто = SQLite. |
| `TRUSTED_PROXY_COUNT` | — | Сколько прокси перед Django дописывают `X-Forwarded-For`: nginx → gunicorn = `1`, без прокси = `0`. Нужна для лимитов по реальному IP, см. «Безопасность». |
| `SECURE_SSL_REDIRECT` | — | `True` по умолчанию. `False`, если HTTPS-редирект делает nginx или балансировщик. |
| `SERVE_MEDIA` | — | `True`: Django сам отдаёт `/media/`. `False`, если `/media/` раздаёт nginx (рекомендуется). |
| `CACHE_DIR` | — | Каталог файлового кэша для лимитов запросов. По умолчанию системный temp. |
| `ENABLE_DJANGO_ADMIN` | — | Стандартная Django-админка `/dashboard-ctrl-panel/`. По умолчанию выключена в production. |

### Фронтенд

[`Front/.env.example`](Front/.env.example): `VITE_API_URL` задаётся **на этапе сборки**. Пусто означает `/api` на том же домене (рекомендуется).

---

## Production-развёртывание (пример: Linux + nginx + gunicorn)

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

Для постоянной работы gunicorn запускается как systemd-сервис, переменные задаются через `Environment=` в unit-файле.

### 2. Фронтенд

```bash
cd Front
npm ci
npm run build          # результат в Front/dist
```

### 3. nginx

```nginx
server {
    listen 443 ssl http2;
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

### 4. Резервные копии

- База данных: `pg_dump`, по расписанию.
- `back/media/`: загруженные картинки товаров, брендов, категорий и баннеров. В git они не хранятся.

---

## Тесты и проверки

```bash
cd back
DEBUG=True python manage.py test api config        # 131 тест
DEBUG=True python manage.py makemigrations --check --dry-run
pip-audit -r requirements.txt                      # (pip install pip-audit)

cd ../Front
npm run build                                      # включает проверку типов vue-tsc
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

Подробно: `docs/superpowers/specs/`.

- **Без собственного `SECRET_KEY`, при `DEBUG` по умолчанию и без `ALLOWED_HOSTS` production не запустится.** Ключи, когда-либо попадавшие в репозиторий, отклоняются всегда.
- **JWT только для staff:** при входе и при каждом обновлении токена. Refresh-токены ротируются. «Выйти» отзывает refresh-токен. Смена пароля отзывает все сессии и все ранее выданные access-токены.
- **Лимиты по реальному IP:** вход 5 в час; отзывы, вопросы и сообщения вместе 30 в час; заказы 20 в час. Подмена `X-Forwarded-For` не обходит лимиты, если `TRUSTED_PROXY_COUNT` задан верно.
- **Заказы:** цена, название и артикул берутся из каталога на сервере, а не от клиента. Не больше 50 позиций, количество от 1 до 999.
- **Отзывы и вопросы** появляются на сайте только после публикации в админ-панели. Длина текстов ограничена.
- **Загрузка картинок:** проверка по содержимому (JPEG, PNG, GIF, WebP; до 10 МБ и 60 Мп), случайные имена файлов, SVG и HTML запрещены. Загружать может только staff.
- **CSV-экспорт заказов** экранирует формулы Excel.
- **Ссылки баннеров:** только `http(s)`, `mailto`, `tel`, `tg`, `viber` или относительные.
- **Зависимости** проверены `pip-audit`, известных уязвимостей нет.

### Известные ограничения

- Тексты «О нас», новостей, брендов и описаний товаров выводятся через `v-html`, то есть HTML из админки исполняется на сайте. Вводить их может только staff. Если админов будет несколько или контент будет приходить из внешних источников, стоит добавить санитизацию (например, DOMPurify).
- Медиафайлы хранятся на локальном диске (`back/media/`). При нескольких серверах нужно общее хранилище (S3 и т.п.).
- Стандартная Django-админка не ограничивает число попыток входа, поэтому в production она выключена (`ENABLE_DJANGO_ADMIN=False`).
