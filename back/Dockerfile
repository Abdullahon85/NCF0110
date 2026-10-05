# Django REST API (gunicorn). Build context: back/
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    CACHE_DIR=/app/cache

WORKDIR /app

RUN useradd --create-home --uid 1000 app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Static files for the Django admin (served by WhiteNoise). DEBUG=True only for this
# build step, so settings load without production secrets.
RUN DEBUG=True python manage.py collectstatic --noinput \
    && mkdir -p /app/media /app/cache \
    && chown -R app:app /app/media /app/cache \
    && chmod +x /app/docker-entrypoint.sh

USER app

EXPOSE 8000

ENTRYPOINT ["/app/docker-entrypoint.sh"]
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "60", "--access-logfile", "-"]
