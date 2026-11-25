# NCF in ONE container: Vue site + admin panel + Django REST API (gunicorn) + SQLite.
# Build context: repository root.   docker compose up -d --build
# Persistent data (database + uploaded images) lives in /data -> mount a volume there.

# ---- 1. Build the Vue site ----
FROM node:22-bookworm-slim AS front
WORKDIR /front
COPY Front/package.json Front/package-lock.json ./
RUN npm ci --no-audit --no-fund
COPY Front/ .
# The API is always on the same domain in this layout: /api
ENV VITE_API_URL=
RUN npm run build

# ---- 2. Django + the built site ----
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    SQLITE_PATH=/data/db.sqlite3 \
    MEDIA_ROOT=/data/media \
    FRONTEND_DIR=/app/frontend \
    SERVE_MEDIA=True \
    CACHE_DIR=/app/cache \
    WEB_CONCURRENCY=3

WORKDIR /app

RUN useradd --create-home --uid 1000 app

COPY back/requirements.txt .
RUN pip install -r requirements.txt

COPY back/ .
COPY --from=front /front/dist /app/frontend

# - collectstatic: CSS/JS of the Django admin (WhiteNoise). DEBUG=True only for this
#   build step, so settings load without production secrets.
# - whitenoise.compress: pre-gzipped copies of the site files.
# - sed: the entrypoint must have Unix line endings even if checked out on Windows.
RUN DEBUG=True python manage.py collectstatic --noinput \
    && python -m whitenoise.compress /app/frontend \
    && sed -i 's/\r$//' /app/docker-entrypoint.sh \
    && chmod +x /app/docker-entrypoint.sh \
    && mkdir -p /data/media /app/cache \
    && chown -R app:app /data /app/cache

USER app

VOLUME ["/data"]
EXPOSE 8000

ENTRYPOINT ["/app/docker-entrypoint.sh"]
# Worker count: WEB_CONCURRENCY (gunicorn reads it itself).
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--timeout", "60", "--access-logfile", "-"]
