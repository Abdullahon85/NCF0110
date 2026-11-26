"""Pages for buyers ("Оплата", "Доставка", "Гарантия"...), edited in the admin panel."""

from django.contrib.auth.models import User
from django.core.cache import caches
from django.test import TestCase
from rest_framework.test import APIClient

from .models import InfoPage


class InfoPagesTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.staff = User.objects.create_user("staff", password="pw-staff-123", is_staff=True)
        InfoPage.objects.create(title="Доставка", content="Текст", order=2)
        InfoPage.objects.create(title="Оплата", content="Текст", order=1)
        InfoPage.objects.create(title="Черновик", content="", is_published=False)

    def setUp(self):
        for c in caches.all(initialized_only=False):
            c.clear()
        self.admin = APIClient()
        self.admin.force_authenticate(self.staff)

    def test_public_list_only_published_in_order(self):
        data = self.client.get("/api/pages/").json()
        self.assertEqual(
            data, [{"slug": "oplata", "title": "Оплата"}, {"slug": "dostavka", "title": "Доставка"}]
        )

    def test_public_detail_and_hidden_draft(self):
        r = self.client.get("/api/pages/dostavka/")
        self.assertEqual((r.status_code, r.json()["content"]), (200, "Текст"))
        self.assertEqual(self.client.get("/api/pages/chernovik/").status_code, 404)

    def test_admin_crud_and_slug_from_title(self):
        self.assertEqual(len(self.admin.get("/api/admin/pages/").json()["results"]), 3)
        r = self.admin.post(
            "/api/admin/pages/", {"title": "Гарантия", "content": "12 мес"}, format="json"
        )
        self.assertEqual(r.status_code, 201, r.data)
        self.assertEqual(r.data["slug"], "garantiya")
        r = self.admin.patch(
            f"/api/admin/pages/{r.data['id']}/", {"is_published": False}, format="json"
        )
        self.assertEqual(r.status_code, 200)
        self.assertEqual(self.client.get("/api/pages/garantiya/").status_code, 404)

    def test_admin_only(self):
        self.assertIn(self.client.get("/api/admin/pages/").status_code, (401, 403))
        self.assertIn(
            self.client.post(
                "/api/pages/", {"title": "x"}, content_type="application/json"
            ).status_code,
            (401, 403, 405),
        )
