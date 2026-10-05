#!/bin/sh
# Wait for the database, apply migrations, then start the given command (gunicorn by default).
set -e

tries=0
until python manage.py migrate --noinput; do
    tries=$((tries + 1))
    if [ "$tries" -ge 30 ]; then
        echo "Database is still unavailable after 60s, giving up." >&2
        exit 1
    fi
    echo "Database not ready, retrying in 2s ($tries/30)..." >&2
    sleep 2
done

exec "$@"
