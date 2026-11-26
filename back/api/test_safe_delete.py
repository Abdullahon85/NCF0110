"""Deleting a category or a brand must never silently take products with it."""

from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.test import APIClient

from .models import Brand, Category, Product


class SafeDeleteTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.staff = User.objects.create_user("admin", password="x", is_staff=True)

    def setUp(self):
        self.admin = APIClient()
        self.admin.force_authenticate(self.staff)

    def delete(self, kind, obj):
        return self.admin.delete(f"/api/admin/{kind}/{obj.id}/")

    def test_category_with_products_not_deleted(self):
        cat = Category.objects.create(name="C", slug="c")
        Product.objects.create(name="P", slug="p", description="d", category=cat)
        response = self.delete("categories", cat)
        self.assertEqual(response.status_code, 400)
        self.assertIn("товар", response.json()["detail"])
        self.assertTrue(Product.objects.filter(slug="p").exists())

    def test_category_with_children_not_deleted(self):
        cat = Category.objects.create(name="C", slug="c")
        Category.objects.create(name="Sub", slug="sub", parent=cat)
        response = self.delete("categories", cat)
        self.assertEqual(response.status_code, 400)
        self.assertIn("подкаталог", response.json()["detail"])
        self.assertEqual(Category.objects.count(), 2)

    def test_subcategory_with_products_blocked_even_if_parent_empty(self):
        cat = Category.objects.create(name="C", slug="c")
        sub = Category.objects.create(name="Sub", slug="sub", parent=cat)
        Product.objects.create(name="P", slug="p", description="d", category=sub)
        self.assertEqual(self.delete("categories", sub).status_code, 400)
        self.assertEqual(self.delete("categories", cat).status_code, 400)
        self.assertEqual(Product.objects.count(), 1)

    def test_empty_category_deleted(self):
        cat = Category.objects.create(name="C", slug="c")
        self.assertEqual(self.delete("categories", cat).status_code, 204)
        self.assertFalse(Category.objects.exists())

    def test_brand_with_products_not_deleted(self):
        cat = Category.objects.create(name="C", slug="c")
        brand = Brand.objects.create(name="B", slug="b")
        Product.objects.create(name="P", slug="p", description="d", category=cat, brand=brand)
        response = self.delete("brands", brand)
        self.assertEqual(response.status_code, 400)
        self.assertIn("товар", response.json()["detail"])
        self.assertTrue(Brand.objects.filter(pk=brand.pk).exists())

    def test_empty_brand_deleted(self):
        brand = Brand.objects.create(name="B", slug="b")
        self.assertEqual(self.delete("brands", brand).status_code, 204)
