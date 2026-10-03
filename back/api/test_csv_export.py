"""Orders CSV export must not let customer input run as spreadsheet formulas (audit item 4)."""
from django.contrib.auth.models import User
from django.test import SimpleTestCase, TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from .csv_safety import safe_csv_cell
from .models import Order


class SafeCsvCellTest(SimpleTestCase):
    def test_formula_prefixed(self):
        self.assertEqual(safe_csv_cell('=HYPERLINK("http://x")'), '\'=HYPERLINK("http://x")')
        self.assertEqual(safe_csv_cell("@SUM(A1)"), "'@SUM(A1)")
        self.assertEqual(safe_csv_cell("-2+3"), "'-2+3")
        self.assertEqual(safe_csv_cell("\t=1"), "'\t=1")
        self.assertEqual(safe_csv_cell("\r=1"), "'\r=1")
        self.assertEqual(safe_csv_cell("+cmd|' /C calc'!A0"), "'+cmd|' /C calc'!A0")

    def test_phone_number_unchanged(self):
        self.assertEqual(safe_csv_cell("+998 90 123-45-67"), "+998 90 123-45-67")
        self.assertEqual(safe_csv_cell("+998(90)1234567"), "+998(90)1234567")

    def test_plain_text_and_non_strings_unchanged(self):
        self.assertEqual(safe_csv_cell("Иван"), "Иван")
        self.assertEqual(safe_csv_cell(""), "")
        self.assertEqual(safe_csv_cell(5), 5)


class OrdersCsvExportTest(TestCase):
    def test_export_escapes_customer_fields(self):
        Order.objects.create(customer_name='=cmd|"/c calc"!A1', customer_phone="+998 90 123-45-67",
                             comment="+SUM(1)")
        api = APIClient()
        api.force_authenticate(User.objects.create_user("staff", password="pw-staff-123", is_staff=True))
        resp = api.get(reverse("export-orders-csv"))
        self.assertEqual(resp.status_code, 200)
        body = resp.content.decode("utf-8-sig")
        self.assertIn("'=cmd", body)
        self.assertIn("'+SUM(1)", body)
        self.assertIn(",+998 90 123-45-67,", body)

    def test_export_requires_staff(self):
        self.assertEqual(APIClient().get(reverse("export-orders-csv")).status_code, 401)
