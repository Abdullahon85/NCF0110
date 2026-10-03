"""Helpers for reading configuration from environment variables.

Pure functions: they take the environment mapping explicitly so they can be
unit-tested without touching os.environ or Django settings.
"""
import os
import re
from pathlib import Path
from typing import Mapping
from urllib.parse import parse_qsl, unquote, urlsplit

from django.core.exceptions import ImproperlyConfigured
from django.core.management.utils import get_random_secret_key

# Keys that were ever committed to the repository. Never accept them.
LEAKED_SECRET_KEYS = frozenset({
    "django-insecure-zo(g8-19uk$1amqpb5obk!@=)fdt-=mv7n3voxe-#zhz#k!0x(",
})

MIN_SECRET_KEY_LENGTH = 50

_TRUE = {"1", "true", "yes", "on"}
_FALSE = {"0", "false", "no", "off", ""}


def env_bool(name: str, default: bool, environ: Mapping[str, str] = os.environ) -> bool:
    if name not in environ:
        return default
    value = environ[name].strip().lower()
    if value in _TRUE:
        return True
    if value in _FALSE:
        return False
    raise ImproperlyConfigured(f"{name} must be a boolean (true/false), got {environ[name]!r}")


def env_list(name: str, default: list[str], environ: Mapping[str, str] = os.environ) -> list[str]:
    if name not in environ:
        return list(default)
    return [item.strip() for item in environ[name].split(",") if item.strip()]


def resolve_secret_key(environ: Mapping[str, str], debug: bool) -> str:
    key = environ.get("SECRET_KEY", "")
    if key in LEAKED_SECRET_KEYS:
        raise ImproperlyConfigured("SECRET_KEY is a leaked key from the repository; generate a new one.")
    if not key:
        # Render sets RENDER=true: never run a deployed instance on a throwaway key.
        if debug and "RENDER" not in environ:
            # Random per process: nothing committed to the repo can sign tokens.
            # Local dev logins reset when the dev server restarts.
            return get_random_secret_key()
        raise ImproperlyConfigured("SECRET_KEY environment variable is required (DEBUG is off or running on Render).")
    if not debug and (key.startswith("django-insecure") or len(key) < MIN_SECRET_KEY_LENGTH):
        raise ImproperlyConfigured(
            f"SECRET_KEY must be at least {MIN_SECRET_KEY_LENGTH} characters and not 'django-insecure' in production."
        )
    return key


DEV_HOSTS = ["localhost", "127.0.0.1"]
DEV_CORS_ORIGINS = ["http://localhost:5173", "http://127.0.0.1:5173"]  # Vite dev server


def build_allowed_hosts(environ: Mapping[str, str], debug: bool) -> list[str]:
    """ALLOWED_HOSTS (comma-separated) from the environment; localhost added in debug.
    Production must list its domains explicitly; '*' is refused (disables Host validation)."""
    hosts = env_list("ALLOWED_HOSTS", [], environ)
    if debug:
        hosts += DEV_HOSTS
    if "*" in hosts:
        raise ImproperlyConfigured("ALLOWED_HOSTS must list real host names; '*' is not allowed.")
    if not hosts:
        raise ImproperlyConfigured("ALLOWED_HOSTS is required when DEBUG is off (e.g. ALLOWED_HOSTS=shop.uz,api.shop.uz).")
    return list(dict.fromkeys(hosts))


_ORIGIN_RE = re.compile(r"https?://[^/\s*]+")


def build_cors_origins(environ: Mapping[str, str], debug: bool) -> list[str]:
    """Frontend origins allowed to call the API from the browser (CORS + CSRF trusted origins).
    CORS_ALLOWED_ORIGINS is comma-separated, each 'scheme://host[:port]' without a path."""
    origins = env_list("CORS_ALLOWED_ORIGINS", [], environ)
    for origin in origins:
        if not _ORIGIN_RE.fullmatch(origin):
            raise ImproperlyConfigured(
                f"CORS_ALLOWED_ORIGINS entry {origin!r} must look like https://shop.uz (no path, no '*')."
            )
    if debug:
        origins += DEV_CORS_ORIGINS
    return list(dict.fromkeys(origins))


_PG_SCHEMES = {"postgres", "postgresql", "pgsql"}


def database_config(environ: Mapping[str, str], base_dir: Path) -> dict:
    """DATABASES['default'] from DATABASE_URL.

    Empty -> SQLite at <base_dir>/db.sqlite3 (local development).
    postgres://user:password@host:port/name?sslmode=require -> PostgreSQL.
    sqlite:////absolute/path.db -> SQLite at that path.
    """
    url = environ.get("DATABASE_URL", "").strip()
    if not url:
        return {"ENGINE": "django.db.backends.sqlite3", "NAME": base_dir / "db.sqlite3"}
    parts = urlsplit(url)
    if parts.scheme == "sqlite":
        path = parts.path[1:]  # sqlite:////abs/path -> /abs/path; sqlite:///rel.db -> rel.db
        if not path:
            raise ImproperlyConfigured("DATABASE_URL sqlite:// needs a file path, e.g. sqlite:////var/data/db.sqlite3")
        return {"ENGINE": "django.db.backends.sqlite3", "NAME": Path(path)}
    if parts.scheme in _PG_SCHEMES:
        name = unquote(parts.path.lstrip("/"))
        if not name:
            raise ImproperlyConfigured("DATABASE_URL must include the database name, e.g. postgres://u:p@host:5432/ncf")
        return {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": name,
            "USER": unquote(parts.username or ""),
            "PASSWORD": unquote(parts.password or ""),
            "HOST": parts.hostname or "",
            "PORT": str(parts.port or ""),
            "OPTIONS": dict(parse_qsl(parts.query)),
            "CONN_MAX_AGE": 60,
        }
    raise ImproperlyConfigured("DATABASE_URL must start with postgres:// (or sqlite:// for SQLite).")
