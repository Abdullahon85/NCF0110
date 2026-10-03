"""Spam protection for public write endpoints (audit item 5)."""
from django.core.cache import caches
from django.test import TestCase
from rest_framework.test import APIClient

from .models import Category, Product


def clear_all_caches():
    for c in caches.all(initialized_only=False):
        c.clear()


class PublicWriteThrottleTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cat = Category.objects.create(name="Cameras", slug="cameras")
        cls.product = Product.objects.create(name="Cam", slug="cam", category=cat, description="d", price=10)

    def setUp(self):
        clear_all_caches()
        self.api = APIClient()

    def _contact(self, xff):
        return self.api.post(
            "/api/contact/message/", {"name": "A", "email": "a@a.uz", "message": "hi"}, format="json",
            REMOTE_ADDR="10.0.0.1", HTTP_X_FORWARDED_FOR=xff,
        )

    def test_31st_public_post_is_throttled(self):
        for _ in range(30):
            self.assertEqual(self._contact("203.0.113.7").status_code, 201)
        self.assertEqual(self._contact("203.0.113.7").status_code, 429)

    def test_spoofed_xff_does_not_bypass(self):
        for i in range(30):
            self._contact(f"1.1.1.{i}, 203.0.113.7")
        self.assertEqual(self._contact("9.9.9.9, 203.0.113.7").status_code, 429)

    def test_bucket_shared_across_endpoints(self):
        for _ in range(30):
            self._contact("203.0.113.7")
        r = self.api.post(
            f"/api/products/{self.product.slug}/reviews/", {"author_name": "A", "rating": 5, "text": "ok"},
            format="json", REMOTE_ADDR="10.0.0.1", HTTP_X_FORWARDED_FOR="203.0.113.7",
        )
        self.assertEqual(r.status_code, 429)

    def test_reading_is_not_throttled(self):
        for _ in range(30):
            self._contact("203.0.113.7")
        r = self.api.get(
            f"/api/products/{self.product.slug}/reviews/", REMOTE_ADDR="10.0.0.1", HTTP_X_FORWARDED_FOR="203.0.113.7",
        )
        self.assertEqual(r.status_code, 200)

    def test_staff_order_management_not_limited(self):
        from django.contrib.auth.models import User
        from .models import Order
        order = Order.objects.create(customer_name="A", customer_phone="1")
        self.api.force_authenticate(User.objects.create_user("staff", password="pw-staff-123", is_staff=True))
        for i in range(31):
            r = self.api.patch(f"/api/orders/{order.id}/", {"status": "processing" if i % 2 else "new"},
                               format="json", REMOTE_ADDR="10.0.0.1", HTTP_X_FORWARDED_FOR="203.0.113.7")
            self.assertEqual(r.status_code, 200, f"request {i + 1}")
