"""Lists that the frontend shows without page switching must return every row,
not only the first page of 12 (DRF's default)."""
from django.contrib.auth.models import User
from django.core.cache import caches
from django.test import TestCase
from rest_framework.test import APIClient

from .models import (Brand, Category, ContactMessage, Image, NewsItem, Product,
                     ProductQuestion, ProductReview, Tag, TagName)

N = 15


class AllRowsTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.staff = User.objects.create_user("admin", password="x", is_staff=True)
        cat = Category.objects.create(name="Base", slug="base")
        product = Product.objects.create(name="P", slug="p", description="d", category=cat)
        for i in range(N):
            Category.objects.create(name=f"Sub {i}", slug=f"sub-{i}", parent=cat)
            Category.objects.create(name=f"Root {i}", slug=f"root-{i}")
            Brand.objects.create(name=f"B{i}", slug=f"b{i}")
            Tag.objects.create(name=f"T{i}", slug=f"t{i}", category=cat)
            TagName.objects.create(name=f"G{i}", category=cat)
            NewsItem.objects.create(title=f"N{i}", slug=f"n{i}", content="c", preview="p")
            Image.objects.create(product=product)
            ContactMessage.objects.create(name="a", email="a@a.uz", message="m")
            ProductReview.objects.create(product=product, author_name="a", rating=5, text="t")
            ProductQuestion.objects.create(product=product, author_name="a", text="t")

    def setUp(self):
        for cache in caches.all():
            cache.clear()
        self.admin = APIClient()
        self.admin.force_authenticate(self.staff)

    @staticmethod
    def rows(response):
        data = response.json()
        return data["results"] if isinstance(data, dict) else data

    def test_admin_lists_return_all_items(self):
        expected = {
            "/api/admin/categories/": 2 * N + 1, "/api/admin/brands/": N, "/api/admin/tags/": N,
            "/api/admin/tag-names/": N, "/api/admin/news/": N, "/api/admin/images/": N,
            "/api/admin/messages/": N, "/api/admin/reviews/": N, "/api/admin/questions/": N,
        }
        for url, count in expected.items():
            with self.subTest(url=url):
                self.assertEqual(len(self.rows(self.admin.get(url))), count)

    def test_public_root_categories_all(self):
        self.assertEqual(len(self.rows(self.client.get("/api/categories/"))), N + 1)

    def test_header_limit_still_works(self):
        self.assertEqual(len(self.rows(self.client.get("/api/categories/?limit=5"))), 5)

    def test_public_news_page_shows_all(self):
        self.assertEqual(len(self.rows(self.client.get("/api/news/"))), N)
        self.assertEqual(len(self.rows(self.client.get("/api/news/?limit=3"))), 3)
