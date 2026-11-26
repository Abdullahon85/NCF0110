"""Tag groups become characteristics, tags become their values (one filter system, like shop.nag.uz).

Each tag group linked to a product becomes Feature(name=group, category=the product's category,
because the product form and the filters work with characteristics of the product's own category;
a group without a name becomes "Теги"); each tag becomes FeatureValue(category, tag name);
the product gets a ProductFeature per tag. Existing characteristics and values with the same
names are reused. Tags that no product uses filtered nothing and are not carried over.
"""

from django.db import migrations


def tags_to_features(apps, schema_editor):
    from api.numbers import parse_number

    Group = apps.get_model("api", "ProductTagGroup")
    Feature = apps.get_model("api", "Feature")
    FeatureValue = apps.get_model("api", "FeatureValue")
    ProductFeature = apps.get_model("api", "ProductFeature")

    groups = Group.objects.select_related("group_name", "product").prefetch_related("tags")
    for group in groups:
        category_id = group.product.category_id
        name = (group.group_name.name if group.group_name else "").strip() or "Теги"
        feature, _ = Feature.objects.get_or_create(name=name, category_id=category_id)
        for tag in group.tags.all():
            value, created = FeatureValue.objects.get_or_create(
                category_id=category_id, value=tag.name
            )
            if created:  # historical models have no custom save(): fill the number here
                value.number = parse_number(tag.name)
                value.save(update_fields=["number"])
            feature.values.add(value)
            ProductFeature.objects.get_or_create(
                product_id=group.product_id, feature=feature, value=value
            )


class Migration(migrations.Migration):
    dependencies = [("api", "0044_feature_filters")]

    operations = [migrations.RunPython(tags_to_features, migrations.RunPython.noop)]
