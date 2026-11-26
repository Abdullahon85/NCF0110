"""Catalog filter module: /api/products/ and /api/products/facets/ (filters like shop.nag.uz)."""

from decimal import Decimal

from django.core.cache import caches
from django.db import connection
from django.test import TestCase
from django.test.utils import CaptureQueriesContext

from .models import (
    Brand,
    Category,
    Feature,
    FeatureValue,
    Order,
    OrderItem,
    Product,
    ProductFeature,
)


class CatalogBase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.root = Category.objects.create(name="Камеры", slug="kamery")
        cls.ip = Category.objects.create(name="IP", slug="ip", parent=cls.root)
        cls.an = Category.objects.create(name="Аналог", slug="analog", parent=cls.root)
        cls.empty = Category.objects.create(name="Пусто", slug="pusto")
        a = Brand.objects.create(name="Alpha", slug="alpha")
        b = Brand.objects.create(name="Beta", slug="beta")

        def feature(cat, name, ftype, *values):
            f = Feature.objects.create(category=cat, name=name, filter_type=ftype)
            vals = {}
            for v in values:
                vals[v] = FeatureValue.objects.create(category=cat, value=v)
                f.values.add(vals[v])
            return f, vals

        cls.color_ip, civ = feature(cls.ip, "Цвет", "list", "Черный", "Белый")
        cls.color_an, cav = feature(cls.an, "Цвет", "list", "Черный")
        cls.res_ip, riv = feature(cls.ip, "Разрешение", "range", "2", "8", "N/A")
        cls.res_an, rav = feature(cls.an, "Разрешение", "range", "5")
        cls.poe, pv = feature(cls.ip, "PoE", "bool", "Нет", "Да")
        cls.black_ids = sorted([civ["Черный"].id, cav["Черный"].id])
        cls.white_id = civ["Белый"].id

        def product(slug, cat, brand, price, links, **extra):
            p = Product.objects.create(
                name=slug,
                slug=slug,
                description="",
                category=cat,
                brand=brand,
                price=price,
                **extra,
            )
            for f, v in links:
                ProductFeature.objects.create(product=p, feature=f, value=v)
            return p

        cls.p1 = product(
            "p1",
            cls.ip,
            a,
            Decimal(100),
            [(cls.color_ip, civ["Черный"]), (cls.res_ip, riv["2"]), (cls.poe, pv["Да"])],
            status="new",
        )
        cls.p2 = product(
            "p2",
            cls.ip,
            b,
            Decimal(200),
            [(cls.color_ip, civ["Белый"]), (cls.res_ip, riv["8"]), (cls.poe, pv["Нет"])],
            old_price=Decimal(250),
        )
        cls.p3 = product(
            "p3",
            cls.an,
            a,
            None,
            [(cls.color_an, cav["Черный"]), (cls.res_an, rav["5"])],
            is_available=False,
        )
        cls.p4 = product(
            "p4",
            cls.ip,
            a,
            Decimal(300),
            [(cls.color_ip, civ["Черный"]), (cls.res_ip, riv["N/A"])],
            status="promo",
            is_recommended=True,
        )
        order = Order.objects.create(customer_name="x", customer_phone="1")
        OrderItem.objects.create(order=order, product=cls.p2, product_name="p2", quantity=5)
        OrderItem.objects.create(order=order, product=cls.p4, product_name="p4", quantity=1)

    def setUp(self):
        for c in caches.all(initialized_only=False):
            c.clear()

    def slugs(self, **params):
        r = self.client.get("/api/products/", params)
        self.assertEqual(r.status_code, 200, r.content)
        return [p["slug"] for p in r.json()["results"]]

    def facets(self, **params):
        r = self.client.get("/api/products/facets/", params)
        self.assertEqual(r.status_code, 200, r.content)
        return r.json()

    def feature_facet(self, data, name):
        return next(f for f in data["features"] if f["name"] == name)


class CatalogFilterTest(CatalogBase):
    def test_or_within_and_across_groups(self):
        color = self.color_ip.id
        ids = ",".join(map(str, [*self.black_ids, self.white_id]))
        self.assertEqual(
            sorted(self.slugs(category="kamery", **{f"f{color}": ids})), ["p1", "p2", "p3", "p4"]
        )
        black = ",".join(map(str, self.black_ids))
        self.assertEqual(
            sorted(self.slugs(category="kamery", brand="alpha", **{f"f{color}": black})),
            ["p1", "p3", "p4"],
        )
        self.assertEqual(self.slugs(category="kamery", **{f"f{color}": str(self.white_id)}), ["p2"])

    def test_same_named_features_merge_on_parent(self):
        data = self.facets(category="kamery")
        colors = [f for f in data["features"] if f["name"] == "Цвет"]
        self.assertEqual(len(colors), 1)
        self.assertEqual(colors[0]["id"], min(self.color_ip.id, self.color_an.id))
        values = {v["value"]: (sorted(v["ids"]), v["count"]) for v in colors[0]["values"]}
        self.assertEqual(values, {"Черный": (self.black_ids, 3), "Белый": ([self.white_id], 1)})

    def test_counts_exclude_own_group(self):
        data = self.facets(category="kamery", brand="alpha")
        self.assertEqual({b["slug"]: b["count"] for b in data["brands"]}, {"alpha": 3, "beta": 1})
        values = {v["value"]: v["count"] for v in self.feature_facet(data, "Цвет")["values"]}
        self.assertEqual(values, {"Черный": 3, "Белый": 0})
        self.assertEqual(data["total"], 3)

    def test_range_filter_and_bounds(self):
        res = min(self.res_ip.id, self.res_an.id)
        facet = self.feature_facet(self.facets(category="kamery"), "Разрешение")
        self.assertEqual((facet["type"], facet["min"], facet["max"]), ("range", 2.0, 8.0))
        self.assertEqual(
            sorted(self.slugs(category="kamery", **{f"f{res}_min": "5"})), ["p2", "p3"]
        )
        self.assertEqual(
            sorted(self.slugs(category="kamery", **{f"f{res}_max": "abc"})),
            ["p1", "p2", "p3", "p4"],
        )

    def test_bool_facet_yes_first(self):
        facet = self.feature_facet(self.facets(category="ip"), "PoE")
        self.assertEqual(facet["type"], "bool")
        self.assertEqual([v["value"] for v in facet["values"]], ["Да", "Нет"])

    def test_price_bounds_ignore_price_filter(self):
        data = self.facets(category="kamery", price_min="150")
        self.assertEqual(data["price"], {"min": 100.0, "max": 300.0})
        self.assertEqual(data["total"], 2)

    def test_promo_recommended_status_stock(self):
        self.assertEqual(sorted(self.slugs(promo="1")), ["p2", "p4"])
        self.assertEqual(self.slugs(recommended="1"), ["p4"])
        self.assertEqual(self.slugs(status="new"), ["p1"])
        self.assertNotIn("p3", self.slugs(in_stock="1"))
        data = self.facets(category="kamery")
        self.assertEqual(data["in_stock"], 3)
        self.assertEqual(
            data["statuses"],
            [
                {"value": "new", "label": "Новинка", "count": 1},
                {"value": "promo", "label": "Акция", "count": 1},
            ],
        )
        self.assertEqual(
            data["categories"],
            [
                {"slug": "ip", "name": "IP", "count": 3},
                {"slug": "analog", "name": "Аналог", "count": 1},
            ],
        )

    def test_ordered_only_for_the_popular_tab(self):
        self.assertEqual(self.slugs(ordered="1"), ["p2", "p4"])

    def test_search(self):
        self.assertEqual(self.slugs(q="p3"), ["p3"])

    def test_sort_popular_and_price_nulls_last(self):
        self.assertEqual(self.slugs(), ["p2", "p4", "p3", "p1"])
        self.assertEqual(self.slugs(sort="price"), ["p1", "p2", "p4", "p3"])
        self.assertEqual(self.slugs(sort="-price"), ["p4", "p2", "p1", "p3"])
        self.assertEqual(self.slugs(sort="new"), ["p4", "p3", "p2", "p1"])

    def test_garbage_params_ignored(self):
        garbage = {
            "f999": "abc",
            "price_min": "abc",
            "page_size": "7",
            "sort": "hack",
            "tag": "x",
            "ordering": "x",
            "f12_min": "zz",
        }
        self.assertEqual(self.slugs(**garbage), self.slugs())
        self.assertEqual(self.client.get("/api/products/facets/", garbage).status_code, 200)

    def test_page_beyond_last_returns_last(self):
        r = self.client.get("/api/products/", {"page": "99", "page_size": "20"}).json()
        self.assertEqual((r["page"], r["page_size"], r["count"], len(r["results"])), (1, 20, 4, 4))

    def test_empty_category_and_brand_facets(self):
        for params in ({"category": "pusto"}, {"category": "net-takogo"}):
            data = self.facets(**params)
            self.assertEqual(data["total"], 0, params)
            self.assertEqual((data["brands"], data["features"], data["statuses"]), ([], [], []))
        # an unknown brand: nothing found, the other brands stay selectable (own group excluded)
        data = self.facets(brand="nobody")
        self.assertEqual((data["total"], data["features"]), (0, []))
        self.assertEqual(self.slugs(brand="nobody"), [])

    def test_query_count_constant(self):
        def count():
            with CaptureQueriesContext(connection) as ctx:
                self.facets(category="kamery")
            return len(ctx.captured_queries)

        before = count()
        for i in range(20):
            Product.objects.create(name=f"x{i}", slug=f"x{i}", description="", category=self.ip)
        self.assertEqual(count(), before)


class CategoryAncestorsTest(CatalogBase):
    def test_detail_has_ancestors_from_root(self):
        sub = Category.objects.create(name="Купольные", slug="kupolnye", parent=self.ip)
        data = self.client.get(f"/api/categories/{sub.slug}/").json()
        self.assertEqual(
            data["ancestors"],
            [
                {"name": "Камеры", "slug": "kamery"},
                {"name": "IP", "slug": "ip"},
            ],
        )
        self.assertEqual(self.client.get("/api/categories/kamery/").json()["ancestors"], [])


class SharedYesValueTest(CatalogBase):
    """«Да» is one FeatureValue row per category, shared by every yes/no characteristic."""

    def test_yes_on_one_feature_does_not_match_yes_on_another(self):
        wifi = Feature.objects.create(category=self.ip, name="Wi-Fi", filter_type="bool")
        yes = FeatureValue.objects.get(category=self.ip, value="Да")
        no = FeatureValue.objects.get(category=self.ip, value="Нет")
        ProductFeature.objects.create(product=self.p2, feature=wifi, value=yes)  # PoE = Нет
        ProductFeature.objects.create(product=self.p1, feature=wifi, value=no)
        self.assertEqual(self.slugs(category="ip", **{f"f{self.poe.id}": str(yes.id)}), ["p1"])
        self.assertEqual(self.slugs(category="ip", **{f"f{wifi.id}": str(yes.id)}), ["p2"])
