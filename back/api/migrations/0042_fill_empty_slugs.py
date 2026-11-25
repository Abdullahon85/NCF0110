"""Rows created before the slug fix may have an empty slug (Cyrillic names were
dropped by slugify). Give each of them a transliterated, unique slug."""
from django.db import migrations

from api.slugs import make_slug, unique_slug

# model name -> (field the slug is built from, max_length, must be unique)
SLUGGED = {
    "Category": ("name", 200, True),
    "Brand": ("name", 160, True),
    "Product": ("name", 200, True),
    "NewsItem": ("title", 200, True),
    "Tag": ("name", 120, False),
}


def fill_empty_slugs(apps, schema_editor):
    for model_name, (source, max_length, unique) in SLUGGED.items():
        model = apps.get_model("api", model_name)
        for obj in model.objects.filter(slug="").order_by("pk"):
            text = getattr(obj, source)
            obj.slug = unique_slug(model, text, max_length, obj.pk) if unique else make_slug(text, max_length)
            obj.save(update_fields=["slug"])


class Migration(migrations.Migration):
    dependencies = [("api", "0041_protect_category_delete")]
    operations = [migrations.RunPython(fill_empty_slugs, migrations.RunPython.noop)]
