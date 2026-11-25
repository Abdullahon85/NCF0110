"""Category tree: subtree walking, cycle safety, parent validation, public subcategory pages."""
from django.contrib.auth.models import User
from django.core.cache import caches
from django.test import TestCase
from rest_framework.test import APIClient

from .categories import subtree_ids
from .models import Category, Product


class CategoryTreeBase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.staff = User.objects.create_user("admin", password="x", is_staff=True)
        cls.root = Category.objects.create(name="Root", slug="root")
        cls.child = Category.objects.create(name="Child", slug="child", parent=cls.root)
        cls.grandchild = Category.objects.create(name="Grand", slug="grand", parent=cls.child)
        cls.other = Category.objects.create(name="Other", slug="other")
        Product.objects.create(name="P", slug="p", description="d", category=cls.grandchild, price=5)

    def setUp(self):
        for cache in caches.all():
            cache.clear()
        self.admin = APIClient()
        self.admin.force_authenticate(self.staff)


class SubtreeTest(CategoryTreeBase):
    def test_subtree_includes_grandchildren(self):
        self.assertEqual(set(subtree_ids([self.root.id])), {self.root.id, self.child.id, self.grandchild.id})

    def test_subtree_terminates_on_existing_cycle(self):
        Category.objects.filter(pk=self.root.pk).update(parent=self.grandchild)
        self.assertEqual(set(subtree_ids([self.root.id])), {self.root.id, self.child.id, self.grandchild.id})

    def test_products_filter_on_cycle_is_200(self):
        Category.objects.filter(pk=self.root.pk).update(parent=self.grandchild)
        response = self.client.get("/api/products/?category=root")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["count"], 1)

    def test_product_detail_on_cycle_is_200(self):
        Category.objects.filter(pk=self.root.pk).update(parent=self.grandchild)
        self.assertEqual(self.client.get("/api/products/p/").status_code, 200)


class ParentValidationTest(CategoryTreeBase):
    def patch_parent(self, category, parent):
        return self.admin.patch(f"/api/admin/categories/{category.id}/", {"parent": parent.id}, format="json")

    def test_parent_cannot_be_self(self):
        response = self.patch_parent(self.root, self.root)
        self.assertEqual(response.status_code, 400)
        self.root.refresh_from_db()
        self.assertIsNone(self.root.parent_id)

    def test_parent_cannot_be_descendant(self):
        response = self.patch_parent(self.root, self.grandchild)
        self.assertEqual(response.status_code, 400)
        self.assertIn("подкаталог", str(response.json()["parent"]))
        self.root.refresh_from_db()
        self.assertIsNone(self.root.parent_id)

    def test_parent_can_be_unrelated(self):
        response = self.patch_parent(self.root, self.other)
        self.assertEqual(response.status_code, 200)
        self.root.refresh_from_db()
        self.assertEqual(self.root.parent_id, self.other.id)


class PublicSubcategoryTest(CategoryTreeBase):
    def test_child_detail_200(self):
        response = self.client.get("/api/categories/child/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["name"], "Child")

    def test_child_products_brands_tags_200(self):
        for action in ("products", "brands", "tags"):
            with self.subTest(action=action):
                self.assertEqual(self.client.get(f"/api/categories/child/{action}/").status_code, 200)
        self.assertEqual(self.client.get("/api/categories/child/products/").json()["count"], 1)

    def test_list_shows_only_roots(self):
        slugs = {c["slug"] for c in self.client.get("/api/categories/").json()["results"]}
        self.assertEqual(slugs, {"root", "other"})

    def test_limit_ignored_on_detail(self):
        self.assertEqual(self.client.get("/api/categories/root/?limit=1").status_code, 200)


class NewsLimitTest(TestCase):
    def test_limit_ignored_on_news_detail(self):
        from .models import NewsItem
        NewsItem.objects.create(title="N", slug="n", content="c", preview="p")
        self.assertEqual(self.client.get("/api/news/n/?limit=1").status_code, 200)
        self.assertEqual(len(self.client.get("/api/news/?limit=1").json()["results"]), 1)


class ModelCleanCycleTest(CategoryTreeBase):
    def test_full_clean_rejects_descendant_parent(self):
        from django.core.exceptions import ValidationError
        self.root.parent = self.grandchild
        with self.assertRaises(ValidationError) as ctx:
            self.root.full_clean()
        self.assertIn("parent", ctx.exception.message_dict)
