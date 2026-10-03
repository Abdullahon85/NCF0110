"""Banner links must not carry script URLs (audit item 9)."""
from django.contrib.auth.models import User
from django.test import SimpleTestCase, TestCase
from rest_framework.exceptions import ValidationError
from rest_framework.test import APIClient

from .models import Banner
from .validators import validate_safe_link


class SafeLinkTest(SimpleTestCase):
    def test_dangerous_links_rejected(self):
        for link in ("javascript:alert(1)", " JaVaScRiPt:alert(1)", "java\tscript:alert(1)",
                     "data:text/html,<script>alert(1)</script>", "vbscript:msgbox(1)"):
            with self.subTest(link=link), self.assertRaises(ValidationError):
                validate_safe_link(link)

    def test_safe_links_allowed(self):
        for link in ("catalog/cameras", "/brands", "#promo", "https://ncf.uz/a?b=1", "http://x.uz",
                     "tel:+998901234567", " /brands ", "", None):
            with self.subTest(link=link):
                self.assertEqual(validate_safe_link(link), link.strip() if link else link)


class BannerLinkApiTest(TestCase):
    def test_admin_banner_api_rejects_javascript(self):
        banner = Banner.objects.create(title="Promo", link="/brands")
        api = APIClient()
        api.force_authenticate(User.objects.create_user("staff", password="pw-staff-123", is_staff=True))
        r = api.patch(f"/api/admin/banners/{banner.id}/", {"link": "javascript:alert(1)"}, format="json")
        self.assertEqual(r.status_code, 400)
        banner.refresh_from_db()
        self.assertEqual(banner.link, "/brands")
