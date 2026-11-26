"""Single-container mode: Vue routes get index.html, API and media keep their own handlers."""

import tempfile
from pathlib import Path

from django.test import TestCase, override_settings


class SpaIndexTest(TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        Path(self.tmp.name, "index.html").write_text("<div id=app>NCF</div>", encoding="utf-8")

    def test_vue_routes_get_index_html(self):
        with override_settings(FRONTEND_DIR=self.tmp.name):
            for url in ("/", "/catalog", "/product/5", "/admin/login"):
                with self.subTest(url=url):
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, 200)
                    self.assertContains(response, "NCF")
                    self.assertEqual(response["Cache-Control"], "no-cache")

    def test_api_assets_and_media_are_not_swallowed(self):
        with override_settings(FRONTEND_DIR=self.tmp.name):
            for url in ("/api/no-such-endpoint/", "/assets/js/missing.js", "/media/missing.png"):
                with self.subTest(url=url):
                    self.assertEqual(self.client.get(url).status_code, 404)

    def test_disabled_without_frontend_dir(self):
        with override_settings(FRONTEND_DIR=""):
            self.assertEqual(self.client.get("/catalog").status_code, 404)

    def test_only_get_and_head(self):
        with override_settings(FRONTEND_DIR=self.tmp.name):
            self.assertEqual(self.client.post("/catalog").status_code, 405)
