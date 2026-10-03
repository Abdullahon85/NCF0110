"""Uploaded images are validated by content, not by client-supplied type (audit item 6)."""
import io
import shutil
import tempfile

from django.contrib.auth.models import User
from django.core.cache import caches
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import SimpleTestCase, TestCase, override_settings
from PIL import Image as PILImage
from rest_framework.test import APIClient

from .models import Category, Image, Product
from .uploads import MAX_UPLOAD_SIZE, validate_uploaded_image

SVG_WITH_SCRIPT = b'<svg xmlns="http://www.w3.org/2000/svg"><script>alert(1)</script></svg>'
HTML_PAYLOAD = b"<html><script>alert(1)</script></html>"


def make_upload(fmt="PNG", size=(10, 10), name="a.png", content_type="image/png", mode="RGB"):
    buf = io.BytesIO()
    PILImage.new(mode, size).save(buf, format=fmt)
    return SimpleUploadedFile(name, buf.getvalue(), content_type=content_type)


class ValidateUploadedImageTest(SimpleTestCase):
    def test_real_png_accepted_and_renamed(self):
        f = make_upload(name="evil.html")
        self.assertEqual(validate_uploaded_image(f), (True, None))
        self.assertTrue(f.name.endswith(".png"))
        self.assertNotIn("evil", f.name)

    def test_html_disguised_as_png_rejected(self):
        f = SimpleUploadedFile("x.png", HTML_PAYLOAD, content_type="image/png")
        self.assertFalse(validate_uploaded_image(f)[0])

    def test_svg_rejected(self):
        f = SimpleUploadedFile("x.svg", SVG_WITH_SCRIPT, content_type="image/svg+xml")
        self.assertFalse(validate_uploaded_image(f)[0])

    def test_truncated_image_rejected(self):
        data = make_upload().read()[:60]
        self.assertFalse(validate_uploaded_image(SimpleUploadedFile("x.png", data, content_type="image/png"))[0])

    def test_unsupported_format_rejected(self):
        self.assertFalse(validate_uploaded_image(make_upload(fmt="BMP", name="x.bmp", content_type="image/bmp"))[0])

    def test_oversize_rejected(self):
        self.assertFalse(validate_uploaded_image(SimpleUploadedFile("x.png", b"0" * (MAX_UPLOAD_SIZE + 1)))[0])

    def test_too_many_pixels_rejected(self):
        self.assertFalse(validate_uploaded_image(make_upload(size=(8000, 8000), mode="1"))[0])

    def test_large_phone_photo_accepted(self):
        f = make_upload(fmt="JPEG", size=(4000, 3000), name="IMG_1.jpg", content_type="image/jpeg")
        self.assertTrue(validate_uploaded_image(f)[0])


    def test_multi_picture_jpeg_from_phone_accepted(self):
        # Phones often embed a secondary image (MPF); Pillow reports such JPEGs as "MPO".
        buf = io.BytesIO()
        PILImage.new("RGB", (64, 48)).save(buf, format="MPO", save_all=True,
                                           append_images=[PILImage.new("RGB", (32, 24))])
        f = SimpleUploadedFile("IMG_2.jpg", buf.getvalue(), content_type="image/jpeg")
        self.assertEqual(validate_uploaded_image(f), (True, None))
        self.assertTrue(f.name.endswith(".jpg"))

class UploadEndpointsTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cat = Category.objects.create(name="Cameras", slug="cameras")
        cls.product = Product.objects.create(name="Cam", slug="cam", category=cat, description="d", price=10)
        cls.staff = User.objects.create_user("staff", password="pw-staff-123", is_staff=True)
        cls.user = User.objects.create_user("user", password="pw-user-123")

    def setUp(self):
        for c in caches.all(initialized_only=False):
            c.clear()
        self.media = tempfile.mkdtemp()
        self.override = override_settings(MEDIA_ROOT=self.media)
        self.override.enable()
        self.api = APIClient()
        self.api.force_authenticate(self.staff)

    def tearDown(self):
        self.override.disable()
        shutil.rmtree(self.media, ignore_errors=True)

    def _upload(self, f):
        return self.api.post(f"/api/admin/products/{self.product.id}/upload-image/", {"images": f}, format="multipart")

    def test_admin_upload_rejects_html(self):
        r = self._upload(SimpleUploadedFile("x.png", HTML_PAYLOAD, content_type="image/png"))
        self.assertEqual(r.status_code, 400)
        self.assertEqual(Image.objects.count(), 0)

    def test_admin_upload_accepts_png(self):
        r = self._upload(make_upload(name="photo.png"))
        self.assertEqual(r.status_code, 201, r.data)
        name = Image.objects.get().image.name
        self.assertTrue(name.startswith("products/") and name.endswith(".png"), name)

    def test_public_upload_route_removed(self):
        api = APIClient()
        api.force_authenticate(self.user)
        r = api.post(f"/api/products/{self.product.slug}/upload-image/", {"images": make_upload()}, format="multipart")
        self.assertEqual(r.status_code, 404)

    def test_image_admin_rejects_svg(self):
        f = SimpleUploadedFile("x.svg", SVG_WITH_SCRIPT, content_type="image/svg+xml")
        r = self.api.post("/api/admin/images/", {"product": self.product.id, "image": f}, format="multipart")
        self.assertEqual(r.status_code, 400)

    def test_image_admin_patch_order_still_works(self):
        img = Image.objects.create(product=self.product, image="products/old.svg")
        r = self.api.patch(f"/api/admin/images/{img.id}/", {"order": 3}, format="json")
        self.assertEqual(r.status_code, 200, r.data)
        img.refresh_from_db()
        self.assertEqual(img.order, 3)
