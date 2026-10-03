"""Hardening left over from the security review, verified before handover."""
import io
import shutil
import tempfile

from django.conf import settings
from django.contrib import admin
from django.contrib.auth.models import User
from django.core.cache import caches
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import RequestFactory, SimpleTestCase, TestCase, override_settings
from PIL import Image as PILImage
from rest_framework.exceptions import ValidationError
from rest_framework.test import APIClient

from .auth import revoke_all_refresh_tokens
from .models import Banner, Brand, Category, Image, Product
from .validators import validate_safe_link

PASSWORD = "Str0ng-pass-123"
HTML = b"<html><script>alert(1)</script></html>"


def png(name="a.png"):
    buf = io.BytesIO()
    PILImage.new("RGB", (8, 8)).save(buf, format="PNG")
    return SimpleUploadedFile(name, buf.getvalue(), content_type="image/png")


def html_as_png():
    return SimpleUploadedFile("x.png", HTML, content_type="image/png")


class HandoverBase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.staff = User.objects.create_user("admin", password=PASSWORD, is_staff=True, is_superuser=True)
        cat = Category.objects.create(name="Cameras", slug="cameras")
        cls.category = cat
        cls.product = Product.objects.create(name="Cam", slug="cam", category=cat, description="d", price=10)

    def setUp(self):
        for c in caches.all(initialized_only=False):
            c.clear()
        self.media = tempfile.mkdtemp()
        self.override = override_settings(MEDIA_ROOT=self.media)
        self.override.enable()
        self.api = APIClient()

    def tearDown(self):
        self.override.disable()
        shutil.rmtree(self.media, ignore_errors=True)

    def _login(self):
        return APIClient().post("/api/admin/auth/login/", {"username": "admin", "password": PASSWORD}, format="json").data


class LogoutRobustnessTest(HandoverBase):
    def test_non_object_body_is_400(self):
        self.assertEqual(self.api.post("/api/admin/auth/logout/", [1, 2], format="json").status_code, 400)

    def test_stale_authorization_header_does_not_block_logout(self):
        t = self._login()
        self.api.credentials(HTTP_AUTHORIZATION="Bearer expired.or.garbage")
        self.assertEqual(self.api.post("/api/admin/auth/logout/", {"refresh": t["refresh"]}, format="json").status_code, 200)
        r = APIClient().post("/api/admin/auth/refresh/", {"refresh": t["refresh"]}, format="json")
        self.assertEqual(r.status_code, 401)


class TokenRevocationTest(HandoverBase):
    def test_old_access_token_dies_on_password_change(self):
        t = self._login()
        api = APIClient()
        api.credentials(HTTP_AUTHORIZATION=f"Bearer {t['access']}")
        r = api.post("/api/admin/auth/change-password/", {"old_password": PASSWORD, "new_password": "N3w-strong-pass-456"}, format="json")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(api.get("/api/admin/auth/me/").status_code, 401)
        fresh = APIClient()
        fresh.credentials(HTTP_AUTHORIZATION=f"Bearer {r.data['access']}")
        self.assertEqual(fresh.get("/api/admin/auth/me/").status_code, 200)

    def test_revoke_all_skips_already_revoked_and_uses_constant_queries(self):
        for _ in range(4):
            self._login()
        self.assertEqual(revoke_all_refresh_tokens(self.staff), 4)
        self.assertEqual(revoke_all_refresh_tokens(self.staff), 0)
        for c in caches.all(initialized_only=False):
            c.clear()  # login is limited to 5/hour per IP
        for _ in range(5):
            self._login()
        with self.assertNumQueries(2):
            self.assertEqual(revoke_all_refresh_tokens(self.staff), 5)


class SafeLinkEdgeCasesTest(SimpleTestCase):
    def test_malformed_url_is_validation_error(self):
        with self.assertRaises(ValidationError):
            validate_safe_link("https://[::1")

    def test_messenger_links_allowed(self):
        for link in ("tg://resolve?domain=shop", "viber://chat?number=998901234567", "mailto:a@b.uz"):
            with self.subTest(link=link):
                self.assertEqual(validate_safe_link(link), link)


class UploadEdgeCasesTest(HandoverBase):
    def test_mixed_batch_saves_nothing(self):
        self.api.force_authenticate(self.staff)
        r = self.api.post(f"/api/admin/products/{self.product.id}/upload-image/",
                          {"images": [png(), html_as_png()]}, format="multipart")
        self.assertEqual(r.status_code, 400)
        self.assertEqual(Image.objects.count(), 0)

    def test_brand_logo_via_api_is_validated_and_renamed(self):
        self.api.force_authenticate(self.staff)
        bad = self.api.post("/api/admin/brands/", {"name": "Bad", "logo": html_as_png()}, format="multipart")
        self.assertEqual(bad.status_code, 400)
        ok = self.api.post("/api/admin/brands/", {"name": "Good", "logo": png("evil.html.png")}, format="multipart")
        self.assertEqual(ok.status_code, 201, ok.data)
        name = Brand.objects.get(name="Good").logo.name
        self.assertTrue(name.endswith(".png") and "evil" not in name, name)

    def test_large_photo_saved_from_disk_backed_upload(self):
        # > FILE_UPLOAD_MAX_MEMORY_SIZE is streamed to a temp file by Django; must still validate.
        buf = io.BytesIO()
        PILImage.effect_noise((1600, 1200), 64).convert("RGB").save(buf, format="JPEG", quality=95)
        data = buf.getvalue()
        self.assertGreater(len(data), 1024 * 1024)
        self.api.force_authenticate(self.staff)
        with override_settings(FILE_UPLOAD_MAX_MEMORY_SIZE=1024):
            r = self.api.post(f"/api/admin/products/{self.product.id}/upload-image/",
                              {"images": SimpleUploadedFile("big.jpg", data, content_type="image/jpeg")},
                              format="multipart")
        self.assertEqual(r.status_code, 201, r.data)


class DjangoAdminFormsTest(HandoverBase):
    def _form(self, model, data, files):
        request = RequestFactory().get("/")
        request.user = self.staff
        form_class = admin.site._registry[model].get_form(request)
        return form_class(data=data, files=files)

    def test_banner_admin_rejects_javascript_link(self):
        form = self._form(Banner, {"title": "t", "link": "javascript:alert(1)", "order": 0, "is_active": True}, {})
        self.assertFalse(form.is_valid())
        self.assertIn("link", form.errors)

    def test_category_admin_rejects_html_upload(self):
        form = self._form(Category, {"name": "X", "slug": "x", "order": 0}, {"image": html_as_png()})
        self.assertFalse(form.is_valid())
        self.assertIn("image", form.errors)


class OldServerErrorsTest(HandoverBase):
    def test_brand_ordering_by_products_count(self):
        Brand.objects.create(name="A", slug="a")
        for ordering in ("products_count", "-products_count"):
            with self.subTest(ordering=ordering):
                self.assertEqual(self.client.get("/api/brands/", {"ordering": ordering}).status_code, 200)

    def test_brand_price_filter_with_garbage(self):
        self.assertEqual(self.client.get("/api/brands/", {"price_min": "abc", "price_max": "x"}).status_code, 200)

    def test_admin_product_create_with_bad_category_is_400(self):
        self.api.force_authenticate(self.staff)
        r = self.api.post("/api/admin/products/", {"name": "P", "category": 999999, "description": "d"}, format="json")
        self.assertEqual(r.status_code, 400)

    def test_admin_product_update_with_bad_price_is_400(self):
        self.api.force_authenticate(self.staff)
        r = self.api.patch(f"/api/admin/products/{self.product.id}/", {"price": "not-a-number"}, format="json")
        self.assertEqual(r.status_code, 400)


class TestSettingsIsolationTest(SimpleTestCase):
    def test_tests_use_in_memory_caches(self):
        for alias in ("default", "throttle"):
            self.assertEqual(settings.CACHES[alias]["BACKEND"], "django.core.cache.backends.locmem.LocMemCache")
