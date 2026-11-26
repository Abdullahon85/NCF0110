"""Product page data: breadcrumbs, characteristics by group, related products."""

from django.contrib.auth.models import User
from django.core.cache import caches
from django.test import TestCase
from rest_framework.test import APIClient

from .models import Category, Feature, FeatureValue, Product, ProductFeature


class ProductPageTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        root = Category.objects.create(name="Камеры", slug="kamery")
        cls.sub = Category.objects.create(name="IP", slug="ip", parent=root)
        cls.p = Product.objects.create(name="Cam", slug="cam", category=cls.sub, description="d")
        cls.a = Product.objects.create(
            name="Bracket", slug="bracket", category=cls.sub, description=""
        )
        cls.b = Product.objects.create(
            name="Cable", slug="cable", category=cls.sub, description="", is_available=False
        )

        def link(name, group, order, value):
            f, _ = Feature.objects.get_or_create(
                name=name, category=cls.sub, defaults={"group": group, "order": order}
            )
            v = FeatureValue.objects.create(category=cls.sub, value=value)
            ProductFeature.objects.create(product=cls.p, feature=f, value=v)

        link("Разрешение", "Матрица", 1, "4 Мп")
        link("Цвет", "", 0, "Белый")
        link("Объектив", "Матрица", 0, "2.8 мм")
        link("Цвет", "", 0, "Серый")
        cls.staff = User.objects.create_user("staff", password="pw-staff-123", is_staff=True)

    def setUp(self):
        for c in caches.all(initialized_only=False):
            c.clear()

    def test_features_carry_group_for_compare_page(self):
        features = self.client.get("/api/products/cam/").json()["features"]
        groups = {f["feature_name"]: f["group_name"] for f in features}
        self.assertEqual(groups["Разрешение"], "Матрица")
        self.assertEqual(groups["Цвет"], "")

    def test_numbers_get_the_unit_of_the_characteristic(self):
        f = Feature.objects.create(name="ИК-подсветка", category=self.sub, unit="м", group="Корпус")
        for text in ("30", "до 40 м"):
            v = FeatureValue.objects.create(category=self.sub, value=text)
            ProductFeature.objects.create(product=self.p, feature=f, value=v)
        groups = self.client.get("/api/products/cam/").json()["feature_groups"]
        row = next(i for g in groups for i in g["items"] if i["name"] == "ИК-подсветка")
        self.assertEqual(row["values"], ["30 м", "до 40 м"])

    def test_breadcrumbs_root_first(self):
        data = self.client.get("/api/products/cam/").json()
        self.assertEqual(
            data["breadcrumbs"],
            [{"name": "Камеры", "slug": "kamery"}, {"name": "IP", "slug": "ip"}],
        )

    def test_feature_groups(self):
        data = self.client.get("/api/products/cam/").json()
        self.assertEqual(
            data["feature_groups"],
            [
                {"group": "Общие", "items": [{"name": "Цвет", "values": ["Белый", "Серый"]}]},
                {
                    "group": "Матрица",
                    "items": [
                        {"name": "Объектив", "values": ["2.8 мм"]},
                        {"name": "Разрешение", "values": ["4 Мп"]},
                    ],
                },
            ],
        )

    def test_related_set_by_admin_available_first(self):
        api = APIClient()
        api.force_authenticate(self.staff)
        r = api.patch(
            f"/api/admin/products/{self.p.id}/",
            {"related_ids": [self.b.id, self.a.id]},
            format="json",
        )
        self.assertEqual(r.status_code, 200, r.data)
        self.assertEqual(sorted(p["id"] for p in r.data["related"]), sorted([self.a.id, self.b.id]))
        related = self.client.get("/api/products/cam/").json()["related"]
        self.assertEqual([p["slug"] for p in related], ["bracket", "cable"])

    def test_related_rejects_self_and_unknown(self):
        api = APIClient()
        api.force_authenticate(self.staff)
        url = f"/api/admin/products/{self.p.id}/"
        for bad in ([self.p.id], [999999], "x"):
            r = api.patch(url, {"related_ids": bad}, format="json")
            self.assertEqual(r.status_code, 400, bad)
            self.assertIn("related_ids", r.json())
