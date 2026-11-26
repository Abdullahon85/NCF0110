"""Migration 0045: tag groups become characteristics, tags become values, links are kept."""

from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.test import TransactionTestCase

BEFORE = [("api", "0044_feature_filters")]
AFTER = [("api", "0045_tags_to_features")]


class TagsToFeaturesMigrationTest(TransactionTestCase):
    def setUp(self):
        executor = MigrationExecutor(connection)
        executor.migrate(BEFORE)
        apps = executor.loader.project_state(BEFORE).apps
        Category = apps.get_model("api", "Category")
        Product = apps.get_model("api", "Product")
        TagName = apps.get_model("api", "TagName")
        Tag = apps.get_model("api", "Tag")
        Group = apps.get_model("api", "ProductTagGroup")
        Feature = apps.get_model("api", "Feature")
        FeatureValue = apps.get_model("api", "FeatureValue")

        self.a = Category.objects.create(name="A", slug="a")
        b = Category.objects.create(name="B", slug="b")

        def product(slug, cat):
            return Product.objects.create(
                name=slug, slug=slug, description="", category=cat, internal_sku=slug
            )

        p1, p2, p3 = product("p1", self.a), product("p2", self.a), product("p3", b)
        color = TagName.objects.create(name="Цвет", category=self.a)
        black = Tag.objects.create(name="Черный", slug="chernyy", category=self.a, tag_name=color)
        white = Tag.objects.create(name="Белый", slug="belyy", category=self.a, tag_name=color)
        Tag.objects.create(name="Красный", slug="krasnyy", category=self.a, tag_name=color)
        loose = TagName.objects.create(name="Серия", category=None)
        pro = Tag.objects.create(name="Pro", slug="pro", tag_name=loose)

        existing = Feature.objects.create(name="Цвет", category=self.a)
        old_black = FeatureValue.objects.create(category=self.a, value="Черный")
        existing.values.add(old_black)

        Group.objects.create(product=p1, group_name=color).tags.set([black])
        Group.objects.create(product=p2, group_name=color).tags.set([white, black])
        Group.objects.create(product=p3, group_name=loose).tags.set([pro])
        # a group without a name, and a product moved to another category after tagging
        Group.objects.create(product=p3, group_name=None).tags.set([white])
        moved = product("moved", b)
        Group.objects.create(product=moved, group_name=color).tags.set([black])
        self.ids = {
            "p1": p1.id,
            "p2": p2.id,
            "p3": p3.id,
            "b": b.id,
            "existing": existing.id,
            "old_black": old_black.id,
            "moved": moved.id,
        }

        executor = MigrationExecutor(connection)
        executor.loader.build_graph()
        executor.migrate(AFTER)
        self.apps = executor.loader.project_state(AFTER).apps

    def tearDown(self):
        executor = MigrationExecutor(connection)
        executor.loader.build_graph()
        executor.migrate(executor.loader.graph.leaf_nodes())

    def _values(self, product_id):
        PF = self.apps.get_model("api", "ProductFeature")
        return sorted(
            (pf.feature.name, pf.value.value)
            for pf in PF.objects.filter(product_id=product_id).select_related("feature", "value")
        )

    def test_links_moved(self):
        self.assertEqual(self._values(self.ids["p1"]), [("Цвет", "Черный")])
        self.assertEqual(self._values(self.ids["p2"]), [("Цвет", "Белый"), ("Цвет", "Черный")])

    def test_existing_feature_and_value_reused(self):
        Feature = self.apps.get_model("api", "Feature")
        FeatureValue = self.apps.get_model("api", "FeatureValue")
        in_a = {"category_id": self.a.id}
        self.assertEqual(Feature.objects.filter(name="Цвет", **in_a).count(), 1)
        self.assertEqual(Feature.objects.get(name="Цвет", **in_a).id, self.ids["existing"])
        self.assertEqual(FeatureValue.objects.filter(value="Черный", **in_a).count(), 1)
        values = set(
            Feature.objects.get(name="Цвет", **in_a).values.values_list("value", flat=True)
        )
        self.assertEqual(values, {"Черный", "Белый"})  # «Красный» had no products

    def test_group_without_category_uses_product_category(self):
        Feature = self.apps.get_model("api", "Feature")
        self.assertEqual(Feature.objects.get(name="Серия").category_id, self.ids["b"])
        self.assertEqual(
            sorted(self._values(self.ids["p3"])), [("Серия", "Pro"), ("Теги", "Белый")]
        )

    def test_feature_created_in_the_product_category(self):
        PF = self.apps.get_model("api", "ProductFeature")
        link = PF.objects.select_related("feature", "value").get(product_id=self.ids["moved"])
        self.assertEqual(
            (link.feature.category_id, link.value.category_id), (self.ids["b"], self.ids["b"])
        )
