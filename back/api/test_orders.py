"""Order creation must take price/name/SKU from the catalog, never from the client (audit item 3)."""
from decimal import Decimal

from django.contrib.auth.models import User
from django.core.cache import cache
from django.test import TestCase
from rest_framework.test import APIClient

from .models import Category, Order, OrderItem, Product

ORDERS_URL = "/api/orders/"


class OrderPricingTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cat = Category.objects.create(name="Cameras", slug="cameras")
        cls.product = Product.objects.create(
            name="Camera 4K", slug="camera-4k", category=cat, description="d",
            price=Decimal("100.00"), manufacturer_sku="SKU-1",
        )
        cls.no_price = Product.objects.create(
            name="Camera on request", slug="camera-on-request", category=cat, description="d", price=None,
        )
        cls.staff = User.objects.create_user("staff", password="pw-staff-123", is_staff=True)
        cls.user = User.objects.create_user("user", password="pw-user-123")

    def setUp(self):
        cache.clear()
        self.api = APIClient()

    def _item(self, product_id, quantity=1):
        # Same shape as Front/src/views/CartPage.vue submitOrder()
        return {"product": product_id, "product_name": "Fake", "product_sku": "X", "price": "1", "quantity": quantity}

    def _post(self, items, **extra):
        data = {
            "customer_name": "Иван", "customer_phone": "+998901234567", "customer_email": "",
            "customer_telegram": "", "comment": "", "items": items, **extra,
        }
        return self.api.post(ORDERS_URL, data, format="json")

    def test_client_price_and_name_are_ignored(self):
        r = self._post([self._item(self.product.id, quantity=2)])
        self.assertEqual(r.status_code, 201, r.data)
        item = OrderItem.objects.get(order_id=r.data["id"])
        self.assertEqual(
            (item.price, item.product_name, item.product_sku, item.quantity),
            (Decimal("100.00"), "Camera 4K", "SKU-1", 2),
        )
        self.assertEqual(Decimal(str(r.data["items"][0]["price"])), Decimal("100.00"))

    def test_product_without_price_keeps_null(self):
        r = self._post([self._item(self.no_price.id)])
        self.assertEqual(r.status_code, 201, r.data)
        self.assertIsNone(OrderItem.objects.get(order_id=r.data["id"]).price)

    def test_item_without_product_rejected(self):
        for item in ({"product_name": "X", "price": "1", "quantity": 1},
                     {"product": None, "product_name": "X", "price": "1", "quantity": 1}):
            self.assertEqual(self._post([item]).status_code, 400)
        self.assertEqual(Order.objects.count(), 0)

    def test_unknown_product_rejected(self):
        r = self._post([self._item(self.product.id), self._item(999999)])
        self.assertEqual(r.status_code, 400)
        self.assertEqual(Order.objects.count(), 0)

    def test_empty_items_rejected(self):
        self.assertEqual(self._post([]).status_code, 400)
        self.assertEqual(Order.objects.count(), 0)

    def test_too_many_items_rejected(self):
        self.assertEqual(self._post([self._item(self.product.id)] * 51).status_code, 400)
        self.assertEqual(Order.objects.count(), 0)

    def test_quantity_bounds(self):
        self.assertEqual(self._post([self._item(self.product.id, quantity=0)]).status_code, 400)
        self.assertEqual(self._post([self._item(self.product.id, quantity=1000)]).status_code, 400)
        self.assertEqual(self._post([self._item(self.product.id, quantity=999)]).status_code, 201)

    def test_anonymous_cannot_set_status(self):
        r = self._post([self._item(self.product.id)], status="completed")
        self.assertEqual(r.status_code, 201)
        self.assertEqual(Order.objects.get(pk=r.data["id"]).status, "new")

    def test_non_staff_user_cannot_set_status(self):
        self.api.force_authenticate(self.user)
        r = self._post([self._item(self.product.id)], status="completed")
        self.assertEqual(r.status_code, 201)
        self.assertEqual(Order.objects.get(pk=r.data["id"]).status, "new")

    def test_staff_can_patch_status(self):
        order = Order.objects.create(customer_name="A", customer_phone="1")
        self.api.force_authenticate(self.staff)
        r = self.api.patch(f"{ORDERS_URL}{order.id}/", {"status": "processing"}, format="json")
        self.assertEqual(r.status_code, 200, r.data)
        order.refresh_from_db()
        self.assertEqual(order.status, "processing")
