#!/bin/sh
# Single container: the SQLite database is a file on the /data volume, so there is
# no database server to wait for. Apply migrations once, then start gunicorn
# (or whatever command was passed).
set -e

mkdir -p "$(dirname "${SQLITE_PATH:-/data/db.sqlite3}")" "${MEDIA_ROOT:-/data/media}"
python manage.py migrate --noinput

exec "$@"
