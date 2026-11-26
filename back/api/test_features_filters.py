"""Feature group, order, filter type and unit; numeric value of a feature value."""

from decimal import Decimal

from django.contrib.auth.models import User
from django.core.cache import caches
from django.test import SimpleTestCase, TestCase
from rest_framework.test import APIClient

from .models import Category, Feature, FeatureValue
from .numbers import parse_number


class ParseNumberTest(SimpleTestCase):
    def test_values(self):
        cases = {
            "10 000 000": Decimal("10000000"),
            "10 000": Decimal("10000"),
            "1,5 м": Decimal("1.5"),
            "до 100": Decimal("100"),
            "-20…+50": Decimal("-20"),
            "4": Decimal("4"),
            "N/A": None,
            "Да": None,
            "": None,
        }
        for text, expected in cases.items():
            self.assertEqual(parse_number(text), expected, text)


class FeatureFieldsTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.cat = Category.objects.create(name="Камеры")
        cls.staff = User.objects.create_user("staff", password="pw-staff-123", is_staff=True)

    def setUp(self):
        for c in caches.all(initialized_only=False):
            c.clear()
        self.api = APIClient()
        self.api.force_authenticate(self.staff)

    def test_feature_value_number_saved(self):
        v = FeatureValue.objects.create(category=self.cat, value="2,8 мм")
        self.assertEqual(v.number, Decimal("2.8"))
        v.value = "нет"
        v.save()
        self.assertIsNone(v.number)

    def test_admin_feature_accepts_group_order_type_unit(self):
        r = self.api.post(
            "/api/admin/features/",
            {
                "name": "Разрешение",
                "category": self.cat.id,
                "group": "Матрица",
                "order": 2,
                "filter_type": "range",
                "unit": "Мп",
            },
            format="json",
        )
        self.assertEqual(r.status_code, 201, r.data)
        f = Feature.objects.get(pk=r.data["id"])
        self.assertEqual((f.group, f.order, f.filter_type, f.unit), ("Матрица", 2, "range", "Мп"))

    def test_admin_feature_default_type_is_list(self):
        r = self.api.post(
            "/api/admin/features/", {"name": "Цвет", "category": self.cat.id}, format="json"
        )
        self.assertEqual(r.status_code, 201, r.data)
        self.assertEqual(r.data["filter_type"], "list")

    def test_admin_feature_rejects_unknown_type(self):
        r = self.api.post(
            "/api/admin/features/",
            {"name": "X", "category": self.cat.id, "filter_type": "slider"},
            format="json",
        )
        self.assertEqual(r.status_code, 400)
        self.assertIn("filter_type", r.json())
