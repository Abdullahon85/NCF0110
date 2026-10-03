"""Security regression tests (audit items 1-2)."""
import importlib

import django.views.static
from django.conf import settings
from django.test import TestCase, override_settings
from django.urls import Resolver404, clear_url_caches, resolve

import config.urls


def reload_urls() -> None:
    """config.urls reads settings at import time; re-import it after override_settings."""
    importlib.reload(config.urls)
    clear_url_caches()


class HostAndMediaTest(TestCase):
    def tearDown(self):
        reload_urls()

    def test_unknown_host_rejected(self):
        resp = self.client.get("/api/categories/", HTTP_HOST="evil.example")
        self.assertEqual(resp.status_code, 400)

    def test_wildcard_not_in_allowed_hosts(self):
        self.assertNotIn("*", settings.ALLOWED_HOSTS)

    def test_media_url_served_without_debug(self):
        with override_settings(DEBUG=False, SERVE_MEDIA=True):
            reload_urls()
            self.assertEqual(resolve("/media/products/x.jpg").func, django.views.static.serve)

    def test_media_not_served_when_disabled(self):
        with override_settings(DEBUG=False, SERVE_MEDIA=False):
            reload_urls()
            with self.assertRaises(Resolver404):
                resolve("/media/products/x.jpg")
