"""Heavy or malformed query parameters must not blow up queries or crash (audit item 8)."""

from django.core.cache import caches
from django.test import TestCase

from .catalog import MAX_FEATURE_GROUPS, filter_products, parse_catalog_query
from .models import Category, Feature, FeatureValue, Product, ProductFeature


class QueryLimitsTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cat = Category.objects.create(name="Cameras", slug="cameras")
        feature = Feature.objects.create(name="Resolution", category=cat)
        value = FeatureValue.objects.create(category=cat, value="4K")
        for i in range(5):
            p = Product.objects.create(
                name=f"Cam {i}", slug=f"cam-{i}", category=cat, description="d", price=10
            )
            ProductFeature.objects.create(product=p, feature=feature, value=value)

    def setUp(self):
        for c in caches.all(initialized_only=False):
            c.clear()

    def test_feature_filters_capped(self):
        params = {f"f{i}": "1" for i in range(1, 51)}
        query = parse_catalog_query(params)
        self.assertEqual(len(query.lists), MAX_FEATURE_GROUPS)
        sql = str(filter_products(query).query)
        self.assertEqual(sql.count('FROM "api_productfeature"'), MAX_FEATURE_GROUPS)

    def test_non_integer_feature_value_ignored(self):
        self.assertEqual(self.client.get("/api/products/", {"f1": "abc"}).status_code, 200)

    def test_taggroup_param_does_not_crash(self):
        self.assertEqual(
            self.client.get("/api/products/", {"taggroup_color": "red"}).status_code, 200
        )

    def test_negative_limit_does_not_crash(self):
        for url in ("/api/categories/", "/api/news/"):
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url, {"limit": "-1"}).status_code, 200)
