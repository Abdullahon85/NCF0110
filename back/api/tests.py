"""
Integration tests for category and brand filter endpoints.

Covers:
  - Single category filter returns only matching products
  - Multi-category filter (comma-separated slugs) returns union of products
  - Blank/empty slugs in comma-joined params are ignored and never reach DB queries
  - Brand products endpoint respects category filters
  - AllBrands list endpoint respects multi-category filter
"""

from django.test import TestCase
from rest_framework.test import APIClient

from .models import (
    Brand,
    Category,
    Product,
)

# ---------------------------------------------------------------------------
# Shared fixture helper
# ---------------------------------------------------------------------------


class BaseFilterTest(TestCase):
    """Creates a reusable fixture: two categories, two brands, six products."""

    @classmethod
    def setUpTestData(cls):
        cls.client = APIClient()

        # ── Categories ──────────────────────────────────────────────────────
        cls.cat_cameras = Category.objects.create(name="Cameras", slug="cameras")
        cls.cat_access = Category.objects.create(name="Access Control", slug="access-control")

        # ── Brands ──────────────────────────────────────────────────────────
        cls.brand_alpha = Brand.objects.create(name="Alpha", slug="alpha")
        cls.brand_beta = Brand.objects.create(name="Beta", slug="beta")

        # ── Products ─────────────────────────────────────────────────────────
        # cam_a: cameras / alpha  / 4K + PoE
        cls.cam_a = Product.objects.create(
            name="Camera Alpha 4K PoE",
            slug="camera-alpha-4k-poe",
            category=cls.cat_cameras,
            brand=cls.brand_alpha,
            description="desc",
            price=100,
        )

        # cam_b: cameras / beta / 2MP + WiFi
        cls.cam_b = Product.objects.create(
            name="Camera Beta 2MP WiFi",
            slug="camera-beta-2mp-wifi",
            category=cls.cat_cameras,
            brand=cls.brand_beta,
            description="desc",
            price=80,
        )

        # cam_c: cameras / alpha / 4K + WiFi
        cls.cam_c = Product.objects.create(
            name="Camera Alpha 4K WiFi",
            slug="camera-alpha-4k-wifi",
            category=cls.cat_cameras,
            brand=cls.brand_alpha,
            description="desc",
            price=120,
        )

        # acc_a: access-control / alpha  / no tags
        cls.acc_a = Product.objects.create(
            name="Access Panel Alpha",
            slug="access-panel-alpha",
            category=cls.cat_access,
            brand=cls.brand_alpha,
            description="desc",
            price=200,
        )

        # acc_b: access-control / beta / no tags
        cls.acc_b = Product.objects.create(
            name="Access Reader Beta",
            slug="access-reader-beta",
            category=cls.cat_access,
            brand=cls.brand_beta,
            description="desc",
            price=150,
        )

        # cam_d: cameras / beta / 4K  (no interface tag)
        cls.cam_d = Product.objects.create(
            name="Camera Beta 4K",
            slug="camera-beta-4k",
            category=cls.cat_cameras,
            brand=cls.brand_beta,
            description="desc",
            price=95,
        )


# ---------------------------------------------------------------------------
# 1. Product list — category filter
# ---------------------------------------------------------------------------


class CategoryFilterTest(BaseFilterTest):
    def setUp(self):
        self.client = APIClient()

    def _get_slugs(self, response):
        return {p["slug"] for p in response.json()["results"]}

    def test_single_category_returns_only_that_category(self):
        resp = self.client.get("/api/products/", {"category": "cameras"})
        self.assertEqual(resp.status_code, 200)
        slugs = self._get_slugs(resp)
        self.assertIn("camera-alpha-4k-poe", slugs)
        self.assertIn("camera-beta-2mp-wifi", slugs)
        self.assertNotIn("access-panel-alpha", slugs)
        self.assertNotIn("access-reader-beta", slugs)

    def test_other_category_returns_only_that_category(self):
        resp = self.client.get("/api/products/", {"category": "access-control"})
        self.assertEqual(resp.status_code, 200)
        slugs = self._get_slugs(resp)
        self.assertIn("access-panel-alpha", slugs)
        self.assertIn("access-reader-beta", slugs)
        self.assertNotIn("camera-alpha-4k-poe", slugs)

    def test_multi_category_returns_union(self):
        resp = self.client.get("/api/products/", {"category": "cameras,access-control"})
        self.assertEqual(resp.status_code, 200)
        slugs = self._get_slugs(resp)
        self.assertIn("camera-alpha-4k-poe", slugs)
        self.assertIn("access-panel-alpha", slugs)

    def test_blank_slug_in_multi_category_is_ignored(self):
        """A comma-joined value with blank entries (e.g. ',cameras,') must not
        cause empty-string slug lookups that return zero results."""
        resp_clean = self.client.get("/api/products/", {"category": "cameras"})
        # Simulate a blank slug leaking into the param (the .filter(Boolean) guard prevents this
        # on the frontend, but the backend should also tolerate it gracefully).
        resp_padded = self.client.get("/api/products/", {"category": ",cameras,"})
        self.assertEqual(resp_clean.status_code, 200)
        self.assertEqual(resp_padded.status_code, 200)
        # Both should return the same products
        self.assertEqual(
            self._get_slugs(resp_clean),
            self._get_slugs(resp_padded),
            "Blank slugs in category param should be stripped, not silently empty the results",
        )

    def test_unknown_category_slug_returns_empty(self):
        resp = self.client.get("/api/products/", {"category": "nonexistent-category"})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["count"], 0)


# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# 3. Brand products endpoint — category filters
# ---------------------------------------------------------------------------


class BrandProductsFilterTest(BaseFilterTest):
    def setUp(self):
        self.client = APIClient()

    def test_brand_products_category_filter(self):
        """GET /api/brands/<slug>/products/?category=cameras returns only
        camera products belonging to that brand."""
        resp = self.client.get(
            "/api/products/", {"brand": self.brand_alpha.slug, "category": "cameras"}
        )
        self.assertEqual(resp.status_code, 200)
        slugs = {p["slug"] for p in resp.json()["results"]}
        self.assertIn("camera-alpha-4k-poe", slugs)
        self.assertIn("camera-alpha-4k-wifi", slugs)
        # access-control product of alpha must be excluded
        self.assertNotIn("access-panel-alpha", slugs)

    def test_brand_products_multi_category(self):
        """Brand products endpoint with comma-separated categories returns
        products from both categories belonging to that brand."""
        resp = self.client.get(
            "/api/products/",
            {"brand": self.brand_alpha.slug, "category": "cameras,access-control"},
        )
        self.assertEqual(resp.status_code, 200)
        slugs = {p["slug"] for p in resp.json()["results"]}
        self.assertIn("camera-alpha-4k-poe", slugs)
        self.assertIn("camera-alpha-4k-wifi", slugs)
        self.assertIn("access-panel-alpha", slugs)
        # beta products must never appear
        self.assertNotIn("camera-beta-2mp-wifi", slugs)


# ---------------------------------------------------------------------------
# 4. AllBrands list — category filter
# ---------------------------------------------------------------------------


class AllBrandsCategoryFilterTest(BaseFilterTest):
    def setUp(self):
        self.client = APIClient()

    def test_brands_filtered_by_single_category(self):
        """GET /api/brands/?category=cameras returns only brands that have
        products in the cameras category."""
        resp = self.client.get("/api/brands/", {"category": "cameras"})
        self.assertEqual(resp.status_code, 200)
        names = {b["name"] for b in resp.json()["results"]}
        # Both brands have camera products
        self.assertIn("Alpha", names)
        self.assertIn("Beta", names)

    def test_brands_filtered_by_access_control_category(self):
        resp = self.client.get("/api/brands/", {"category": "access-control"})
        self.assertEqual(resp.status_code, 200)
        names = {b["name"] for b in resp.json()["results"]}
        self.assertIn("Alpha", names)
        self.assertIn("Beta", names)

    def test_blank_slug_in_brands_category_param(self):
        """Blank slugs in the brands category param must not silently empty results."""
        resp_clean = self.client.get("/api/brands/", {"category": "cameras"})
        resp_padded = self.client.get("/api/brands/", {"category": ",cameras,"})
        self.assertEqual(resp_clean.status_code, 200)
        self.assertEqual(resp_padded.status_code, 200)
        clean_names = {b["name"] for b in resp_clean.json()["results"]}
        padded_names = {b["name"] for b in resp_padded.json()["results"]}
        self.assertEqual(
            clean_names,
            padded_names,
            "Blank slugs in brands category param must be stripped, not empty the result",
        )
