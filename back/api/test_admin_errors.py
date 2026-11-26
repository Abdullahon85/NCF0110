"""Errors the admin sees are in Russian and name the problem."""

from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.test import APIClient

from .models import Banner, Brand, Category, Product


class AdminErrorsTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.staff = User.objects.create_user("admin", password="x", is_staff=True)

    def setUp(self):
        self.admin = APIClient()
        self.admin.force_authenticate(self.staff)

    def test_duplicate_brand_name_message_in_russian(self):
        Brand.objects.create(name="Hikvision", slug="hikvision")
        response = self.admin.post(
            "/api/admin/brands/", {"name": "Hikvision", "slug": "hik-2"}, format="json"
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("уже существует", str(response.json()["name"]))

    def test_banner_str_without_title(self):
        banner = Banner.objects.create(title=None)
        self.assertEqual(str(banner), f"Баннер #{banner.pk}")

    def test_update_keeps_existing_uppercase_slug(self):
        cat = Category.objects.create(name="C", slug="c")
        product = Product.objects.create(name="Hik", slug="Hik-1", description="d", category=cat)
        response = self.admin.patch(
            f"/api/admin/products/{product.id}/",
            {"name": "Hik 2", "slug": "Hik-1", "category": cat.id},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        product.refresh_from_db()
        self.assertEqual((product.name, product.slug), ("Hik 2", "Hik-1"))
