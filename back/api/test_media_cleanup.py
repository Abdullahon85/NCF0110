"""Image files are removed from disk when their row is deleted or the image is replaced."""
import io
import os
import shutil
import tempfile

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from PIL import Image as PILImage
from rest_framework.test import APIClient

from .models import Banner, Brand, Category, Image, Product


def png(name="a.png"):
    buf = io.BytesIO()
    PILImage.new("RGB", (4, 4)).save(buf, format="PNG")
    return SimpleUploadedFile(name, buf.getvalue(), content_type="image/png")


class MediaCleanupTest(TestCase):
    def setUp(self):
        self.media = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.media, ignore_errors=True)
        override = override_settings(MEDIA_ROOT=self.media)
        override.enable()
        self.addCleanup(override.disable)
        self.cat = Category.objects.create(name="C", slug="c")
        self.product = Product.objects.create(name="P", slug="p", description="d", category=self.cat)

    def exists(self, fieldfile_name):
        return os.path.exists(os.path.join(self.media, fieldfile_name))

    def test_deleting_image_removes_file(self):
        img = Image.objects.create(product=self.product, image=png())
        name = img.image.name
        self.assertTrue(self.exists(name))
        with self.captureOnCommitCallbacks(execute=True):
            img.delete()
        self.assertFalse(self.exists(name))

    def test_deleting_product_removes_its_image_files(self):
        names = [Image.objects.create(product=self.product, image=png()).image.name for _ in range(2)]
        with self.captureOnCommitCallbacks(execute=True):
            self.product.delete()
        self.assertFalse(any(self.exists(n) for n in names))

    def test_replacing_category_image_removes_old_file_keeps_new(self):
        self.cat.image = png("old.png")
        self.cat.save()
        old = self.cat.image.name
        with self.captureOnCommitCallbacks(execute=True):
            self.cat.image = png("new.png")
            self.cat.save()
        self.assertFalse(self.exists(old))
        self.assertTrue(self.exists(self.cat.image.name))

    def test_saving_without_change_keeps_file(self):
        brand = Brand.objects.create(name="B", slug="b", logo=png())
        with self.captureOnCommitCallbacks(execute=True):
            brand.description = "x"
            brand.save()
            Banner.objects.create(title="t", image=png()).save()
        self.assertTrue(self.exists(brand.logo.name))

    def test_delete_image_endpoint_removes_file(self):
        staff = User.objects.create_user("admin", password="x", is_staff=True)
        client = APIClient()
        client.force_authenticate(staff)
        img = Image.objects.create(product=self.product, image=png())
        with self.captureOnCommitCallbacks(execute=True):
            response = client.delete(f"/api/admin/products/{self.product.id}/delete-image/{img.id}/")
        self.assertEqual(response.status_code, 200)
        self.assertFalse(self.exists(img.image.name))
