"""Product documents (паспорт, инструкция...): checked by content, stored under a random name."""

import os
import shutil
import tempfile

from django.contrib.auth.models import User
from django.core.cache import caches
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import SimpleTestCase, TestCase, override_settings
from rest_framework.test import APIClient

from .documents import MAX_DOCUMENT_SIZE, validate_uploaded_document
from .models import Category, Product, ProductDocument

SAMPLES = {
    "a.pdf": b"%PDF-1.7\n...",
    "a.docx": b"PK\x03\x04rest",
    "a.xlsx": b"PK\x03\x04rest",
    "a.zip": b"PK\x03\x04rest",
    "a.doc": bytes.fromhex("D0CF11E0A1B11AE1") + b"rest",
    "a.xls": bytes.fromhex("D0CF11E0A1B11AE1") + b"rest",
    "a.rar": b"Rar!\x1a\x07\x00rest",
}


class ValidateDocumentTest(SimpleTestCase):
    def test_allowed_types_by_signature(self):
        for name, data in SAMPLES.items():
            f = SimpleUploadedFile(name, data)
            self.assertEqual(validate_uploaded_document(f), (True, None), name)
            ext = name.rsplit(".", 1)[1]
            self.assertTrue(f.name.endswith(f".{ext}") and not f.name.startswith("a."), f.name)

    def test_rejected(self):
        bad = {
            "x.pdf": b"<html><script>alert(1)</script>",
            "x.docx": b"%PDF-1.7",
            "x.exe": b"MZ\x90\x00",
            "x.svg": b"<svg/>",
            "x.html": b"<html>",
            "noext": b"%PDF-1.7",
        }
        for name, data in bad.items():
            self.assertFalse(validate_uploaded_document(SimpleUploadedFile(name, data))[0], name)

    def test_too_large(self):
        f = SimpleUploadedFile("big.pdf", b"%PDF" + b"0" * MAX_DOCUMENT_SIZE)
        self.assertFalse(validate_uploaded_document(f)[0])


class DocumentApiTest(TestCase):
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
        self.url = f"/api/admin/products/{self.product.id}/documents/"

    def tearDown(self):
        self.override.disable()
        shutil.rmtree(self.media, ignore_errors=True)

    def _upload(self, client=None):
        f = SimpleUploadedFile("passport.pdf", SAMPLES["a.pdf"])
        return (client or self.api).post(
            self.url, {"title": "Паспорт", "file": f}, format="multipart"
        )

    def test_upload_list_and_delete(self):
        r = self._upload()
        self.assertEqual(r.status_code, 201, r.data)
        doc = ProductDocument.objects.get()
        path = doc.file.path
        self.assertTrue(os.path.exists(path))
        public = self.client.get("/api/products/cam/").json()["documents"]
        self.assertEqual(public[0]["title"], "Паспорт")
        self.assertTrue(public[0]["url"].endswith(".pdf"))
        self.assertEqual(public[0]["ext"], "pdf")
        with self.captureOnCommitCallbacks(execute=True):  # files go after the commit
            r = self.api.delete(f"{self.url}{doc.id}/")
        self.assertEqual(r.status_code, 204)
        self.assertFalse(ProductDocument.objects.exists())
        self.assertFalse(os.path.exists(path))

    def test_bad_file_and_missing_title_400(self):
        f = SimpleUploadedFile("x.pdf", b"<html>")
        self.assertEqual(
            self.api.post(self.url, {"title": "X", "file": f}, format="multipart").status_code, 400
        )
        f = SimpleUploadedFile("a.pdf", SAMPLES["a.pdf"])
        self.assertEqual(
            self.api.post(self.url, {"title": " ", "file": f}, format="multipart").status_code, 400
        )

    def test_only_staff(self):
        self.assertIn(self._upload(APIClient()).status_code, (401, 403))
        user = User.objects.create_user("u", password="pw-user-123")
        client = APIClient()
        client.force_authenticate(user)
        self.assertEqual(self._upload(client).status_code, 403)
