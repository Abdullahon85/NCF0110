"""Bad query parameters and bad admin input answer 400, never 500."""
from django.contrib.auth.models import User
from django.core.cache import caches
from django.test import TestCase
from rest_framework.test import APIClient

from .models import Category, Order, Product


class ParamsBase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.staff = User.objects.create_user("admin", password="x", is_staff=True)
        cls.cat = Category.objects.create(name="C", slug="c")

    def setUp(self):
        for cache in caches.all():
            cache.clear()
        self.admin = APIClient(raise_request_exception=False)
        self.admin.force_authenticate(self.staff)
        self.anon = APIClient(raise_request_exception=False)


class OrderDateFilterTest(ParamsBase):
    def test_orders_bad_date_400(self):
        for param in ("date_from", "date_to"):
            with self.subTest(param=param):
                response = self.admin.get(f"/api/orders/?{param}=abc")
                self.assertEqual(response.status_code, 400)
                self.assertIn(param, response.json())

    def test_csv_bad_date_400(self):
        self.assertEqual(self.admin.get("/api/admin/orders/export-csv/?date_from=31.12.2026").status_code, 400)

    def test_orders_good_date_filters(self):
        Order.objects.create(customer_name="a", customer_phone="1")
        self.assertEqual(self.admin.get("/api/orders/?date_from=2000-01-01").json()["count"], 1)
        self.assertEqual(self.admin.get("/api/orders/?date_to=2000-01-01").json()["count"], 0)
        csv = self.admin.get("/api/admin/orders/export-csv/?date_from=2000-01-01").content.decode()
        self.assertEqual(len(csv.strip().splitlines()), 2)


class NumericParamTest(ParamsBase):
    def test_features_tags_bad_id_400(self):
        self.assertEqual(self.anon.get("/api/features-tags-by-category/?category=abc").status_code, 400)

    def test_feature_values_bad_id_400(self):
        self.assertEqual(self.anon.get("/api/feature-values-by-feature/?feature_id=abc").status_code, 400)

    def test_admin_list_bad_numeric_filter_400(self):
        urls = [
            "/api/admin/products/?category=abc", "/api/admin/products/?brand=abc",
            "/api/admin/categories/?parent=abc", "/api/admin/tags/?category=abc",
            "/api/admin/tags/?tag_name=abc", "/api/admin/tag-names/?category=abc",
            "/api/admin/features/?category=abc", "/api/admin/feature-values/?category=abc",
            "/api/admin/feature-values/?feature=abc", "/api/admin/images/?product=abc",
            "/api/admin/reviews/?product=abc", "/api/admin/reviews/?rating=abc",
            "/api/admin/questions/?product=abc",
        ]
        for url in urls:
            with self.subTest(url=url):
                self.assertEqual(self.admin.get(url).status_code, 400)

    def test_admin_list_good_numeric_filter_200(self):
        self.assertEqual(self.admin.get(f"/api/admin/products/?category={self.cat.id}").status_code, 200)
        self.assertEqual(self.admin.get("/api/admin/categories/?parent=null").status_code, 200)


class ProductAdminInputTest(ParamsBase):
    def create(self, **data):
        payload = {"name": "P", "description": "d", "category": self.cat.id, **data}
        return self.admin.post("/api/admin/products/", payload, format="json")

    def test_product_features_not_list_400(self):
        for key, bad in (("features", "abc"), ("features", ["x"]), ("tag_groups", 5), ("tag_groups", [1])):
            with self.subTest(key=key, bad=bad):
                response = self.create(**{key: bad})
                self.assertEqual(response.status_code, 400)
                self.assertIn(key, response.json())
        self.assertFalse(Product.objects.exists())

    def test_product_update_images_not_list_400(self):
        product_id = self.create().json()["id"]
        response = self.admin.patch(f"/api/admin/products/{product_id}/", {"images": "x"}, format="json")
        self.assertEqual(response.status_code, 400)

    def test_product_without_name_400(self):
        response = self.create(name="  ")
        self.assertEqual(response.status_code, 400)
        self.assertIn("name", response.json())

    def test_product_update_blank_name_400(self):
        product_id = self.create().json()["id"]
        response = self.admin.patch(f"/api/admin/products/{product_id}/", {"name": ""}, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Product.objects.get().name, "P")

    def test_product_without_category_400(self):
        for category in (None, 999999, "abc"):
            with self.subTest(category=category):
                response = self.create(category=category)
                self.assertEqual(response.status_code, 400)
                self.assertIn("category", response.json())


class PriceRangeTest(ParamsBase):
    def test_price_range_zero(self):
        Product.objects.create(name="Free", slug="free", description="d", category=self.cat, price=0)
        Product.objects.create(name="Paid", slug="paid", description="d", category=self.cat, price=50)
        data = self.anon.get("/api/products/price-range/").json()
        self.assertEqual((data["min_price"], data["max_price"]), (0.0, 50.0))


class DeadEndpointsTest(ParamsBase):
    def test_debug_first_removed(self):
        from .models import Feature
        Feature.objects.create(name="F", category=self.cat)  # the old endpoint answered 200 then
        self.assertEqual(self.admin.get("/api/admin/features/debug_first/").status_code, 404)


class OrderUpdateTest(ParamsBase):
    def test_patch_with_items_400_and_status_still_works(self):
        order = Order.objects.create(customer_name="a", customer_phone="1")
        product = Product.objects.create(name="P", slug="p", description="d", category=self.cat)
        response = self.admin.patch(f"/api/orders/{order.id}/", {"items": [{"product": product.id, "quantity": 1}]}, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("items", response.json())
        response = self.admin.patch(f"/api/orders/{order.id}/", {"status": "completed"}, format="json")
        self.assertEqual((response.status_code, response.json()["status"]), (200, "completed"))


class TagsWithCountTest(ParamsBase):
    def test_tags_with_count_200(self):
        from .models import ProductTagGroup, Tag
        tag = Tag.objects.create(name="T", slug="t", category=self.cat)
        product = Product.objects.create(name="P", slug="p", description="d", category=self.cat)
        ProductTagGroup.objects.create(product=product).tags.add(tag)
        response = self.anon.get("/api/tags/with_count/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [{"id": tag.id, "name": "T", "slug": "t", "count": 1}])


class ProductPriceTest(ParamsBase):
    def setUp(self):
        super().setUp()
        self.product = Product.objects.create(name="P", slug="p", description="d", category=self.cat, price=10)

    def test_bad_price_400_and_catalog_still_works(self):
        for price in ("1e999", "1e30", "-5", "12.345", "abc", "nan", "inf"):
            with self.subTest(price=price):
                response = self.admin.patch(f"/api/admin/products/{self.product.id}/", {"price": price}, format="json")
                self.assertEqual(response.status_code, 400)
                self.assertIn("price", response.json())
                self.assertEqual(self.anon.get("/api/products/").status_code, 200)
        self.product.refresh_from_db()
        self.assertEqual(self.product.price, 10)

    def test_bad_price_on_create_400(self):
        response = self.admin.post("/api/admin/products/", {"name": "Q", "description": "d", "category": self.cat.id, "price": "1e999"}, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("price", response.json())

    def test_good_prices(self):
        for price, expected in (("1500000", "1500000.00"), ("99.5", "99.50"), (250, "250.00"), ("", None), (None, None)):
            with self.subTest(price=price):
                response = self.admin.patch(f"/api/admin/products/{self.product.id}/", {"price": price}, format="json")
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.json()["price"], expected)


class ProductLengthTest(ParamsBase):
    def test_too_long_fields_400(self):
        for field, size in (("name", 201), ("manufacturer_sku", 101), ("internal_sku", 101)):
            with self.subTest(field=field):
                data = {"name": "P", "description": "d", "category": self.cat.id, field: "x" * size}
                response = self.admin.post("/api/admin/products/", data, format="json")
                self.assertEqual(response.status_code, 400)
                self.assertIn(field, response.json())
        self.assertFalse(Product.objects.exists())


class ProductUniqueAndRefsTest(ParamsBase):
    def create(self, **extra):
        return self.admin.post("/api/admin/products/", {"name": "P", "description": "d", "category": self.cat.id, **extra}, format="json")

    def test_duplicate_internal_sku_400_with_field(self):
        self.assertEqual(self.create(internal_sku="SKU-1").status_code, 201)
        response = self.create(internal_sku="SKU-1")
        self.assertEqual(response.status_code, 400)
        self.assertIn("internal_sku", response.json())
        other = self.create(internal_sku="SKU-2").json()
        response = self.admin.patch(f"/api/admin/products/{other['id']}/", {"internal_sku": "SKU-1"}, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("internal_sku", response.json())

    def test_unknown_brand_400_with_field(self):
        for brand in (999999, "abc"):
            with self.subTest(brand=brand):
                response = self.create(brand=brand)
                self.assertEqual(response.status_code, 400)
                self.assertIn("brand", response.json())
