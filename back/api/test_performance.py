"""Product lists must not run one query per product (N+1)."""
from django.core.cache import caches
from django.db import connection
from django.test import TestCase
from django.test.utils import CaptureQueriesContext

from .models import Brand, Category, Image, Product, ProductTagGroup, Tag, TagName

MAX_QUERIES = 10


class ProductListQueryCountTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cat = Category.objects.create(name="C", slug="c")
        brand = Brand.objects.create(name="B", slug="b")
        group = TagName.objects.create(name="G", category=cat)
        tag = Tag.objects.create(name="T", slug="t", category=cat, tag_name=group)
        for i in range(12):
            p = Product.objects.create(name=f"P{i}", slug=f"p{i}", description="d", category=cat, brand=brand, price=1)
            Image.objects.create(product=p, is_main=True)
            Image.objects.create(product=p)
            ProductTagGroup.objects.create(product=p, group_name=group).tags.add(tag)

    def setUp(self):
        for cache in caches.all():
            cache.clear()

    def test_product_list_query_count(self):
        for url in ("/api/products/", "/api/categories/c/products/", "/api/brands/b/products/",
                    "/api/products/by-feature/?value=x", "/api/products/p0/similar/"):
            with self.subTest(url=url):
                with CaptureQueriesContext(connection) as queries:
                    response = self.client.get(url)
                self.assertEqual(response.status_code, 200)
                self.assertLessEqual(len(queries), MAX_QUERIES)
