import os
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured
from django.test import SimpleTestCase

from config.env import (
    LEAKED_SECRET_KEYS,
    build_allowed_hosts,
    build_cors_origins,
    cache_dir,
    media_url,
    database_config,
    env_bool,
    env_list,
    resolve_secret_key,
)


class EnvHelpersTest(SimpleTestCase):
    def test_env_bool_parses_variants(self):
        self.assertTrue(env_bool("X", False, {"X": "TRUE"}))
        self.assertFalse(env_bool("X", True, {"X": "off"}))
        self.assertTrue(env_bool("X", True, {}))

    def test_env_bool_rejects_garbage(self):
        with self.assertRaises(ImproperlyConfigured):
            env_bool("X", False, {"X": "maybe"})

    def test_env_list_strips_and_drops_empty(self):
        self.assertEqual(env_list("H", [], {"H": " a.com, ,b.com,"}), ["a.com", "b.com"])

    def test_env_list_default_is_copied(self):
        default = ["a"]
        result = env_list("H", default, {})
        result.append("b")
        self.assertEqual(default, ["a"])

    def test_secret_key_required_in_production(self):
        with self.assertRaises(ImproperlyConfigured):
            resolve_secret_key({}, debug=False)

    def test_dev_fallback_key_is_random_not_committed(self):
        # A fallback committed to the repo would be forgeable like the leaked key.
        first = resolve_secret_key({}, debug=True)
        second = resolve_secret_key({}, debug=True)
        self.assertNotEqual(first, second)
        self.assertGreaterEqual(len(first), 50)

    def test_leaked_key_rejected_even_in_debug(self):
        leaked = next(iter(LEAKED_SECRET_KEYS))
        for debug in (True, False):
            with self.assertRaises(ImproperlyConfigured):
                resolve_secret_key({"SECRET_KEY": leaked}, debug=debug)

    def test_insecure_prefix_rejected_in_production(self):
        with self.assertRaises(ImproperlyConfigured):
            resolve_secret_key({"SECRET_KEY": "django-insecure-" + "a" * 50}, debug=False)

    def test_short_key_rejected_in_production(self):
        with self.assertRaises(ImproperlyConfigured):
            resolve_secret_key({"SECRET_KEY": "x" * 49}, debug=False)

    def test_valid_key_returned(self):
        key = "k" * 50
        self.assertEqual(resolve_secret_key({"SECRET_KEY": key}, debug=False), key)


class AllowedHostsTest(SimpleTestCase):
    def test_production_requires_explicit_hosts(self):
        with self.assertRaises(ImproperlyConfigured):
            build_allowed_hosts({}, debug=False)

    def test_production_hosts_from_env(self):
        self.assertEqual(build_allowed_hosts({"ALLOWED_HOSTS": "shop.uz, api.shop.uz"}, False),
                         ["shop.uz", "api.shop.uz"])

    def test_localhost_only_in_debug(self):
        self.assertNotIn("localhost", build_allowed_hosts({"ALLOWED_HOSTS": "shop.uz"}, False))
        self.assertEqual(build_allowed_hosts({}, True), ["localhost", "127.0.0.1"])

    def test_wildcard_rejected(self):
        with self.assertRaises(ImproperlyConfigured):
            build_allowed_hosts({"ALLOWED_HOSTS": "example.uz,*"}, False)

    def test_no_hosting_specific_hosts(self):
        hosts = build_allowed_hosts({"ALLOWED_HOSTS": "a.uz", "RENDER_EXTERNAL_HOSTNAME": "x.onrender.com",
                                     "REPLIT_DEV_DOMAIN": "x.replit.dev"}, False)
        self.assertEqual(hosts, ["a.uz"])

    def test_no_duplicates(self):
        self.assertEqual(build_allowed_hosts({"ALLOWED_HOSTS": "localhost"}, True).count("localhost"), 1)


class CorsOriginsTest(SimpleTestCase):
    def test_origins_from_env(self):
        self.assertEqual(build_cors_origins({"CORS_ALLOWED_ORIGINS": "https://shop.uz, https://admin.shop.uz"}, False),
                         ["https://shop.uz", "https://admin.shop.uz"])

    def test_empty_in_production_by_default(self):
        self.assertEqual(build_cors_origins({}, False), [])

    def test_vite_dev_server_allowed_in_debug(self):
        self.assertEqual(build_cors_origins({}, True), ["http://localhost:5173", "http://127.0.0.1:5173"])

    def test_invalid_origins_rejected(self):
        for value in ("*", "shop.uz", "https://shop.uz/", "ftp://shop.uz"):
            with self.subTest(value=value), self.assertRaises(ImproperlyConfigured):
                build_cors_origins({"CORS_ALLOWED_ORIGINS": value}, False)


class DatabaseConfigTest(SimpleTestCase):
    BASE = Path("/srv/app")

    def test_sqlite_by_default(self):
        cfg = database_config({}, self.BASE)
        self.assertEqual((cfg["ENGINE"], cfg["NAME"]), ("django.db.backends.sqlite3", self.BASE / "db.sqlite3"))

    def test_postgres_url(self):
        cfg = database_config({"DATABASE_URL": "postgres://shop:p%40ss@db.local:5433/ncf"}, self.BASE)
        self.assertEqual(
            {k: cfg[k] for k in ("ENGINE", "NAME", "USER", "PASSWORD", "HOST", "PORT")},
            {"ENGINE": "django.db.backends.postgresql", "NAME": "ncf", "USER": "shop",
             "PASSWORD": "p@ss", "HOST": "db.local", "PORT": "5433"},
        )
        self.assertEqual(cfg["CONN_MAX_AGE"], 60)

    def test_postgresql_scheme_and_options(self):
        cfg = database_config({"DATABASE_URL": "postgresql://u@h/ncf?sslmode=require"}, self.BASE)
        self.assertEqual((cfg["ENGINE"], cfg["PORT"], cfg["OPTIONS"]),
                         ("django.db.backends.postgresql", "", {"sslmode": "require"}))

    def test_sqlite_url(self):
        cfg = database_config({"DATABASE_URL": "sqlite:////var/data/shop.db"}, self.BASE)
        self.assertEqual((cfg["ENGINE"], str(cfg["NAME"])), ("django.db.backends.sqlite3", "/var/data/shop.db"))

    def test_invalid_urls_rejected(self):
        for url in ("mysql://u:p@h/db", "postgres://u:p@h/", "not a url"):
            with self.subTest(url=url), self.assertRaises(ImproperlyConfigured):
                database_config({"DATABASE_URL": url}, self.BASE)


class CacheDirTest(SimpleTestCase):
    def test_empty_cache_dir_falls_back_to_temp(self):
        import tempfile
        for env in ({}, {"CACHE_DIR": ""}, {"CACHE_DIR": "  "}):
            with self.subTest(env=env):
                self.assertEqual(cache_dir(env), os.path.join(tempfile.gettempdir(), "ncf_django_cache"))

    def test_explicit_cache_dir(self):
        self.assertEqual(cache_dir({"CACHE_DIR": "/var/cache/ncf"}), "/var/cache/ncf")


class MediaUrlTest(SimpleTestCase):
    def test_default_relative(self):
        self.assertEqual(media_url({}), "/media/")

    def test_absolute_for_separate_api_domain(self):
        self.assertEqual(media_url({"MEDIA_URL": "https://api.shop.uz/media"}), "https://api.shop.uz/media/")

    def test_invalid_rejected(self):
        for value in ("media/", "ftp://x/media/"):
            with self.subTest(value=value), self.assertRaises(ImproperlyConfigured):
                media_url({"MEDIA_URL": value})
