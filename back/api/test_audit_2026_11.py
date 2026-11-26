"""Regression tests for the code audit of 25.11.2026."""

import io
import shutil
import tempfile

from django.contrib.auth.models import User
from django.core.cache import caches
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from PIL import Image as PILImage
from rest_framework.test import APIClient

from .models import Category, Image, Product


def _png(name="p.png"):
    buf = io.BytesIO()
    PILImage.new("RGB", (8, 8)).save(buf, format="PNG")
    return SimpleUploadedFile(name, buf.getvalue(), content_type="image/png")


class ProductImagesFromAdminFormTest(TestCase):
    """The product form of the admin panel: removing a photo and choosing a
    newly added photo as the main one must reach the database."""

    @classmethod
    def setUpTestData(cls):
        cat = Category.objects.create(name="Cameras", slug="cameras")
        cls.product = Product.objects.create(name="Cam", slug="cam", category=cat, description="d")
        cls.staff = User.objects.create_user("staff", password="pw-staff-123", is_staff=True)

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

    def _upload(self, **extra):
        return self.api.post(
            f"/api/admin/products/{self.product.id}/upload-image/",
            {"image": _png(), **extra},
            format="multipart",
        )

    def test_new_image_chosen_as_main_becomes_the_only_main(self):
        old = Image.objects.create(
            product=self.product, image="products/old.png", is_main=True, order=0
        )
        r = self._upload(is_main="true", order="1")
        self.assertEqual(r.status_code, 201, r.data)
        new = Image.objects.get(pk=r.data["images"][0]["id"])
        old.refresh_from_db()
        self.assertTrue(new.is_main)
        self.assertEqual(new.order, 1)
        self.assertFalse(old.is_main)

    def test_upload_without_flags_keeps_existing_main(self):
        old = Image.objects.create(product=self.product, image="products/old.png", is_main=True)
        r = self._upload()
        self.assertEqual(r.status_code, 201, r.data)
        old.refresh_from_db()
        self.assertTrue(old.is_main)
        self.assertFalse(Image.objects.get(pk=r.data["images"][0]["id"]).is_main)

    def test_bad_order_is_400(self):
        self.assertEqual(self._upload(order="abc").status_code, 400)

    def test_update_with_delete_flag_removes_image(self):
        keep = Image.objects.create(product=self.product, image="products/a.png")
        gone = Image.objects.create(product=self.product, image="products/b.png")
        r = self.api.patch(
            f"/api/admin/products/{self.product.id}/",
            {
                "images": [
                    {"id": keep.id, "is_main": True, "order": 0},
                    {"id": gone.id, "_delete": True},
                ]
            },
            format="json",
        )
        self.assertEqual(r.status_code, 200, r.data)
        self.assertEqual(list(self.product.images.values_list("id", flat=True)), [keep.id])
