"""Product commerce fields (old price, stock, status, recommended), SKU, fresh public lists."""

from decimal import Decimal

from django.contrib.auth.models import User
from django.core.cache import caches
from django.test import SimpleTestCase, TestCase
from rest_framework.test import APIClient

from .models import Category, Product
from .pricing import discount_percent


class DiscountPercentTest(SimpleTestCase):
    def test_values(self):
        D = Decimal
        self.assertEqual(discount_percent(D(100), D(125)), 20)
        self.assertIsNone(discount_percent(None, D(100)))
        self.assertIsNone(discount_percent(D(100), D(100)))
        self.assertIsNone(discount_percent(D(100), D(90)))
        self.assertIsNone(discount_percent(D(0), D(100)))
        self.assertIsNone(discount_percent(D(100), None))
        self.assertEqual(discount_percent(D("82"), D("100")), 18)


class ProductCommerceApiTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.cat = Category.objects.create(name="Камеры")
        cls.product = Product.objects.create(
            name="Cam",
            slug="cam",
            category=cls.cat,
            description="d",
            price=Decimal("82"),
            old_price=Decimal("100"),
            stock_quantity=9,
            status="sale",
        )
        cls.staff = User.objects.create_user("staff", password="pw-staff-123", is_staff=True)

    def setUp(self):
        for c in caches.all(initialized_only=False):
            c.clear()
        self.admin = APIClient()
        self.admin.force_authenticate(self.staff)

    def test_list_and_detail_expose_commerce_fields(self):
        for url in ("/api/products/", "/api/products/cam/"):
            data = self.client.get(url).json()
            item = data["results"][0] if "results" in data else data
            self.assertEqual(Decimal(item["old_price"]), Decimal("100"))
            self.assertEqual(item["discount_percent"], 18)
            self.assertEqual(item["stock_quantity"], 9)
            self.assertEqual(item["status"], "sale")
            self.assertEqual(item["status_label"], "Распродажа")

    def test_admin_saves_commerce_fields(self):
        r = self.admin.patch(
            f"/api/admin/products/{self.product.id}/",
            {"old_price": "120,50", "stock_quantity": 0, "status": "new", "is_recommended": True},
            format="json",
        )
        self.assertEqual(r.status_code, 200, r.data)
        p = Product.objects.get(pk=self.product.pk)
        self.assertEqual(
            (p.old_price, p.stock_quantity, p.status, p.is_recommended),
            (Decimal("120.50"), 0, "new", True),
        )

    def test_admin_clears_old_price_and_stock(self):
        r = self.admin.patch(
            f"/api/admin/products/{self.product.id}/",
            {"old_price": "", "stock_quantity": None, "status": ""},
            format="json",
        )
        self.assertEqual(r.status_code, 200, r.data)
        p = Product.objects.get(pk=self.product.pk)
        self.assertEqual((p.old_price, p.stock_quantity, p.status), (None, None, ""))

    def test_admin_rejects_bad_status_and_negative_stock(self):
        url = f"/api/admin/products/{self.product.id}/"
        r = self.admin.patch(url, {"status": "hot"}, format="json")
        self.assertEqual(r.status_code, 400)
        self.assertIn("status", r.json())
        r = self.admin.patch(url, {"stock_quantity": -1}, format="json")
        self.assertEqual(r.status_code, 400)
        self.assertIn("stock_quantity", r.json())

    def test_internal_sku_is_prefix_and_pk(self):
        p = Product.objects.create(name="A", category=self.cat, description="")
        self.assertEqual(p.internal_sku, f"KAM-{p.pk:05d}")
        q = Product.objects.create(name="B", category=self.cat, description="")
        self.assertEqual(q.internal_sku, f"KAM-{q.pk:05d}")

    def test_internal_sku_taken_by_hand_gets_suffix(self):
        nxt = Product.objects.order_by("-pk").first().pk + 1
        Product.objects.create(
            name="Manual", category=self.cat, description="", internal_sku=f"KAM-{nxt + 1:05d}"
        )
        p = Product.objects.create(name="Auto", category=self.cat, description="")
        self.assertEqual(p.internal_sku, f"KAM-{p.pk:05d}-2")

    def test_public_lists_not_cached(self):
        self.client.get("/api/categories/")
        Category.objects.filter(pk=self.cat.pk).update(name="Новое имя")
        r = self.client.get("/api/categories/")
        self.assertEqual(r.json()["results"][0]["name"], "Новое имя")
        self.assertNotIn("max-age", r.get("Cache-Control", ""))

    def test_order_accepts_out_of_stock_product(self):
        Product.objects.filter(pk=self.product.pk).update(is_available=False)
        r = self.client.post(
            "/api/orders/",
            {
                "customer_name": "Ali",
                "customer_phone": "+998901234567",
                "items": [{"product": self.product.id, "quantity": 2}],
            },
            content_type="application/json",
        )
        self.assertEqual(r.status_code, 201, r.content)
