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


class ModerationAndLimitsTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        from django.contrib.auth.models import User
        cat = Category.objects.create(name="Cameras", slug="cameras")
        cls.product = Product.objects.create(name="Cam", slug="cam", category=cat, description="d", price=10)
        cls.staff = User.objects.create_user("staff", password="pw-staff-123", is_staff=True)

    def setUp(self):
        clear_all_caches()
        self.api = APIClient()

    def _review(self, text, rating=5):
        return self.api.post("/api/products/cam/reviews/", {"author_name": "A", "rating": rating, "text": text}, format="json")

    def _question(self, text):
        return self.api.post("/api/products/cam/questions/", {"author_name": "A", "text": text}, format="json")

    def _contact(self, message):
        return self.api.post("/api/contact/message/", {"name": "A", "email": "a@a.uz", "message": message}, format="json")

    def _order(self, comment):
        item = {"product": self.product.id, "product_name": "Cam", "product_sku": "", "price": "10", "quantity": 1}
        return self.api.post("/api/orders/", {
            "customer_name": "A", "customer_phone": "+998901234567", "customer_email": "",
            "customer_telegram": "", "comment": comment, "items": [item],
        }, format="json")

    def test_new_review_hidden_until_moderated(self):
        r = self._review(text="ok")
        self.assertEqual((r.status_code, r.data["is_published"]), (201, False))
        self.assertEqual(self.api.get("/api/products/cam/reviews/").data["count"], 0)

    def test_admin_publish_makes_review_visible(self):
        rid = self._review(text="ok").data["id"]
        self.api.force_authenticate(self.staff)
        self.assertEqual(self.api.patch(f"/api/admin/reviews/{rid}/", {"is_published": True}, format="json").status_code, 200)
        self.api.force_authenticate(None)
        self.assertEqual(self.api.get("/api/products/cam/reviews/").data["count"], 1)

    def test_new_question_hidden_until_moderated(self):
        r = self._question(text="ok?")
        self.assertEqual((r.status_code, r.data["is_published"]), (201, False))
        self.assertEqual(self.api.get("/api/products/cam/questions/").data["count"], 0)

    def test_text_length_limits(self):
        self.assertEqual(self._review(text="x" * 2000).status_code, 201)
        self.assertEqual(self._review(text="x" * 2001).status_code, 400)
        self.assertEqual(self._question(text="x" * 1001).status_code, 400)
        self.assertEqual(self._contact(message="x" * 3001).status_code, 400)
        self.assertEqual(self._order(comment="x" * 1001).status_code, 400)
        self.assertEqual(self._order(comment="x" * 1000).status_code, 201)

    def test_review_for_unknown_product_is_404(self):
        r = self.api.post("/api/products/nope/reviews/", {"author_name": "A", "rating": 5, "text": "t"}, format="json")
        self.assertEqual(r.status_code, 404)


class OrderBudgetTest(TestCase):
    """Checkout has its own budget: review/contact spam from a shared IP must not block orders."""

    @classmethod
    def setUpTestData(cls):
        cat = Category.objects.create(name="Cameras", slug="cameras")
        cls.product = Product.objects.create(name="Cam", slug="cam", category=cat, description="d", price=10)

    def setUp(self):
        clear_all_caches()
        self.api = APIClient()
        self.net = {"REMOTE_ADDR": "10.0.0.1", "HTTP_X_FORWARDED_FOR": "203.0.113.7"}

    def _order(self):
        item = {"product": self.product.id, "quantity": 1}
        return self.api.post("/api/orders/", {"customer_name": "A", "customer_phone": "+998901234567",
                                              "items": [item]}, format="json", **self.net)

    def test_review_spam_does_not_block_checkout(self):
        for _ in range(30):
            self.api.post("/api/contact/message/", {"name": "A", "email": "a@a.uz", "message": "hi"},
                          format="json", **self.net)
        self.assertEqual(self._order().status_code, 201)

    def test_order_budget_is_limited(self):
        from .throttles import ORDER_RATE
        limit = int(ORDER_RATE.split("/")[0])
        for i in range(limit):
            self.assertEqual(self._order().status_code, 201, f"order {i + 1}")
        self.assertEqual(self._order().status_code, 429)
