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


class LoginThrottleTest(TestCase):
    """LoginRateThrottle (5/hour) must count the real client IP, not a spoofable header."""

    def setUp(self):
        from django.core.cache import cache
        from rest_framework.test import APIClient
        cache.clear()
        self.api = APIClient()

    def _login(self, xff):
        from django.urls import reverse
        extra = {"REMOTE_ADDR": "10.0.0.1"}
        if xff is not None:
            extra["HTTP_X_FORWARDED_FOR"] = xff
        return self.api.post(
            reverse("admin-login"), {"username": "nobody", "password": "wrong"}, format="json", **extra
        )

    def test_spoofed_xff_does_not_bypass_limit(self):
        for i in range(5):
            self.assertEqual(self._login(xff=f"1.2.3.{i}, 203.0.113.7").status_code, 401)
        self.assertEqual(self._login(xff="9.9.9.9, 203.0.113.7").status_code, 429)

    def test_other_real_client_not_blocked(self):
        for _ in range(5):
            self._login(xff="203.0.113.7")
        self.assertEqual(self._login(xff="203.0.113.8").status_code, 401)

    def test_no_proxy_header_uses_remote_addr(self):
        for _ in range(5):
            self._login(xff=None)
        self.assertEqual(self._login(xff=None).status_code, 429)
