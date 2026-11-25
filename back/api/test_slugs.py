"""Slugs: always non-empty ASCII, unique, transliterated from Russian/Uzbek names."""
import importlib

from django.apps import apps
from django.contrib.auth.models import User
from django.test import SimpleTestCase, TestCase
from rest_framework.test import APIClient

from .models import Brand, Category, NewsItem, Product, Tag
from .slugs import make_slug


class MakeSlugTest(SimpleTestCase):
    def test_cyrillic_name_gets_ascii_slug(self):
        self.assertEqual(make_slug("Камеры", 200), "kamery")

    def test_uzbek_letters(self):
        self.assertEqual(make_slug("Ўзбек қовун", 200), "ozbek-qovun")

    def test_latin_apostrophe(self):
        self.assertEqual(make_slug("O‘zbekiston", 200), "ozbekiston")
        self.assertEqual(make_slug("G'isht", 200), "gisht")

    def test_symbols_only_name_not_empty(self):
        self.assertEqual(make_slug("!!!", 200), "item")

    def test_max_length(self):
        self.assertEqual(len(make_slug("а" * 300, 200)), 200)


class ModelSlugTest(TestCase):
    def test_duplicate_names_get_suffix(self):
        cat = Category.objects.create(name="Камеры")
        other = Category.objects.create(name="Камеры")
        self.assertEqual((cat.slug, other.slug), ("kamery", "kamery-2"))
        p1 = Product.objects.create(name="Камера X", description="d", category=cat)
        p2 = Product.objects.create(name="Камера X", description="d", category=cat)
        self.assertEqual((p1.slug, p2.slug), ("kamera-x", "kamera-x-2"))

    def test_every_model_fills_slug(self):
        self.assertEqual(Brand.objects.create(name="Ўзбек").slug, "ozbek")
        self.assertEqual(NewsItem.objects.create(title="Новость", content="c", preview="p").slug, "novost")
        self.assertEqual(Tag.objects.create(name="Уличная").slug, "ulichnaya")

    def test_migration_fills_empty_slugs(self):
        cat = Category.objects.create(name="Камеры", slug="kamery")
        Category.objects.filter(pk=cat.pk).update(slug="")
        Product.objects.create(name="Камера", slug="kamera", description="d", category=cat)
        Product.objects.filter(slug="kamera").update(slug="")
        migration = importlib.import_module("api.migrations.0042_fill_empty_slugs")
        migration.fill_empty_slugs(apps, None)
        cat.refresh_from_db()
        self.assertEqual(cat.slug, "kamery")
        self.assertEqual(Product.objects.get().slug, "kamera")


class AdminProductSlugTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.staff = User.objects.create_user("admin", password="x", is_staff=True)
        cls.cat = Category.objects.create(name="C", slug="c")

    def setUp(self):
        self.admin = APIClient()
        self.admin.force_authenticate(self.staff)

    def create(self, **extra):
        data = {"name": "Камера X", "slug": "kamera-x", "description": "d", "category": self.cat.id, **extra}
        return self.admin.post("/api/admin/products/", data, format="json")

    def test_admin_create_duplicate_slug_201(self):
        self.assertEqual(self.create().status_code, 201)
        response = self.create()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["slug"], "kamera-x-2")

    def test_admin_create_without_slug(self):
        response = self.create(slug="")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["slug"], "kamera-x")

    def test_admin_update_to_taken_slug_400(self):
        self.create()
        other = self.create(name="Y", slug="y").json()
        response = self.admin.patch(f"/api/admin/products/{other['id']}/", {"slug": "kamera-x"}, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("занят", str(response.json()["slug"]))
        self.assertEqual(Product.objects.get(pk=other["id"]).slug, "y")
