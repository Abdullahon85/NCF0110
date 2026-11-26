"""Remove uploaded image files from disk when they are no longer used.

Django deletes the database row but leaves the file, so the media folder (the
ncf-data volume in Docker) would keep growing. A file is deleted when its row is
deleted or when the field gets a different file, and only after the database
transaction commits (a rolled-back delete keeps its file).
"""

from django.db import transaction
from django.db.models.signals import post_delete, pre_save

from .models import Banner, Brand, Category, Image, ProductDocument

FILE_FIELDS = {
    Image: "image",
    Category: "image",
    Brand: "logo",
    Banner: "image",
    ProductDocument: "file",
}


def _delete_after_commit(storage, name):
    if name:
        transaction.on_commit(lambda: storage.delete(name))


def delete_file_with_row(sender, instance, **kwargs):
    fieldfile = getattr(instance, FILE_FIELDS[sender])
    _delete_after_commit(fieldfile.storage, fieldfile.name)


def delete_replaced_file(sender, instance, **kwargs):
    if instance.pk is None:
        return
    field = FILE_FIELDS[sender]
    old_name = sender.objects.filter(pk=instance.pk).values_list(field, flat=True).first()
    new_file = getattr(instance, field)
    if old_name and old_name != (new_file.name or None):
        _delete_after_commit(new_file.storage, old_name)


for model in FILE_FIELDS:
    post_delete.connect(
        delete_file_with_row, sender=model, dispatch_uid=f"media-delete-{model.__name__}"
    )
    pre_save.connect(
        delete_replaced_file, sender=model, dispatch_uid=f"media-replace-{model.__name__}"
    )
