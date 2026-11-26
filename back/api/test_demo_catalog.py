"""`manage.py demo_catalog`: a demo section to see the filters and the product page at work."""

import shutil
import tempfile

from django.core.cache import caches
from django.core.management import call_command
from django.test import TestCase, override_settings

from .models import Brand, Category, Feature, Product, ProductDocument


class DemoCatalogTest(TestCase):
    def setUp(self):
        for c in caches.all(initialized_only=False):
            c.clear()
        self.media = tempfile.mkdtemp()
        self.override = override_settings(MEDIA_ROOT=self.media)
        self.override.enable()

    def tearDown(self):
        self.override.disable()
        shutil.rmtree(self.media, ignore_errors=True)

    def test_creates_a_section_with_every_kind_of_filter(self):
        call_command("demo_catalog", verbosity=0)
        root = Category.objects.get(slug="demo-videonablyudenie")
        self.assertGreaterEqual(root.children.count(), 2)
        self.assertGreaterEqual(Product.objects.filter(slug__startswith="demo-").count(), 12)
        types = set(
            Feature.objects.filter(category__parent=root).values_list("filter_type", flat=True)
        )
        self.assertTrue({"list", "bool", "range"} <= types)

        data = self.client.get("/api/products/facets/", {"category": root.slug}).json()
        self.assertEqual({f["type"] for f in data["features"]}, {"list", "bool", "range"})
        self.assertTrue(data["brands"] and data["statuses"] and data["categories"])

        product = Product.objects.filter(slug__startswith="demo-", related__isnull=False).first()
        page = self.client.get(f"/api/products/{product.slug}/").json()
        self.assertTrue(page["related"] and page["feature_groups"])
        self.assertTrue(ProductDocument.objects.filter(product__slug__startswith="demo-").exists())
        self.assertTrue(
            Product.objects.filter(slug__startswith="demo-", old_price__isnull=False).exists()
        )
        self.assertTrue(
            Product.objects.filter(slug__startswith="demo-", is_available=False).exists()
        )

    def test_running_twice_does_not_duplicate(self):
        call_command("demo_catalog", verbosity=0)
        counts = (Product.objects.count(), Feature.objects.count(), ProductDocument.objects.count())
        call_command("demo_catalog", verbosity=0)
        self.assertEqual(
            (Product.objects.count(), Feature.objects.count(), ProductDocument.objects.count()),
            counts,
        )

    def test_remove_deletes_only_demo(self):
        own = Category.objects.create(name="Свой раздел", slug="svoy")
        Product.objects.create(name="Свой товар", slug="svoy-tovar", category=own, description="")
        call_command("demo_catalog", verbosity=0)
        call_command("demo_catalog", "--remove", verbosity=0)
        self.assertFalse(Product.objects.filter(slug__startswith="demo-").exists())
        self.assertFalse(Category.objects.filter(slug__startswith="demo-").exists())
        self.assertFalse(Brand.objects.filter(slug__startswith="demo-").exists())
        self.assertTrue(Product.objects.filter(slug="svoy-tovar").exists())
