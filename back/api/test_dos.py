"""Heavy or malformed query parameters must not blow up queries or crash (audit item 8)."""
from django.core.cache import caches
from django.test import TestCase
from rest_framework.request import Request
from rest_framework.test import APIRequestFactory

from .models import Category, Feature, FeatureValue, Product, ProductFeature
from .views import MAX_BY_FEATURE_RESULTS, MAX_FEATURE_FILTERS, apply_product_filters


class QueryLimitsTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cat = Category.objects.create(name="Cameras", slug="cameras")
        feature = Feature.objects.create(name="Resolution", category=cat)
        value = FeatureValue.objects.create(category=cat, value="4K")
        for i in range(MAX_BY_FEATURE_RESULTS + 5):
            p = Product.objects.create(name=f"Cam {i}", slug=f"cam-{i}", category=cat, description="d", price=10)
            ProductFeature.objects.create(product=p, feature=feature, value=value)

    def setUp(self):
        for c in caches.all(initialized_only=False):
            c.clear()

    def test_feature_filters_capped(self):
        params = {f"feature_{i}": "1" for i in range(1, 51)}
        request = Request(APIRequestFactory().get("/api/products/", params))
        sql = str(apply_product_filters(request, Product.objects.all()).query)
        self.assertEqual(sql.count('JOIN "api_productfeature"'), MAX_FEATURE_FILTERS)

    def test_non_integer_feature_value_ignored(self):
        self.assertEqual(self.client.get("/api/products/", {"feature_1": "abc"}).status_code, 200)

    def test_taggroup_param_does_not_crash(self):
        self.assertEqual(self.client.get("/api/products/", {"taggroup_color": "red"}).status_code, 200)

    def test_negative_limit_does_not_crash(self):
        for url in ("/api/categories/", "/api/news/"):
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url, {"limit": "-1"}).status_code, 200)

    def test_by_feature_results_capped(self):
        r = self.client.get("/api/products/by-feature/", {"value": "4K"})
        self.assertEqual((r.status_code, len(r.data)), (200, MAX_BY_FEATURE_RESULTS))
