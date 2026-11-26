"""Demo section "Видеонаблюдение (демо)" to see the catalog filters and the product page at work.

    python manage.py demo_catalog            # create or refresh (safe to run again)
    python manage.py demo_catalog --remove   # delete everything it created

Everything it creates has a slug starting with "demo-" and "(демо)" in its name; the
shop's own data is never touched. Brands and texts are invented for the demo.
"""

from decimal import Decimal

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.db import transaction

from api.models import (
    Brand,
    Category,
    Feature,
    FeatureValue,
    Product,
    ProductDocument,
    ProductFeature,
)

ROOT = ("demo-videonablyudenie", "Видеонаблюдение (демо)")
SUBS = {
    "ip": ("demo-ip-kamery", "IP-камеры (демо)"),
    "an": ("demo-analogovye-kamery", "Аналоговые камеры (демо)"),
    "nvr": ("demo-videoregistratory", "Видеорегистраторы (демо)"),
}
BRANDS = {
    "lumera": "Lumera (демо)",
    "ostrix": "Ostrix (демо)",
    "vigilo": "Vigilo (демо)",
}

# name: (filter type, table group, order, unit)
CAMERA_FEATURES = {
    "Тип корпуса": ("list", "Корпус", 1, ""),
    "Цвет": ("list", "Корпус", 2, ""),
    "Уличная": ("bool", "Корпус", 3, ""),
    "ИК-подсветка": ("range", "Корпус", 4, "м"),
    "Разрешение": ("range", "Матрица", 1, "Мп"),
    "Объектив": ("list", "Матрица", 2, ""),
}
FEATURES = {
    "ip": {
        **CAMERA_FEATURES,
        "PoE": ("bool", "Сеть", 1, ""),
        "Wi-Fi": ("bool", "Сеть", 2, ""),
        "Микрофон": ("bool", "Сеть", 3, ""),
    },
    "an": {**CAMERA_FEATURES, "Формат сигнала": ("list", "Сигнал", 1, "")},
    "nvr": {
        "Каналов": ("range", "", 1, "шт"),
        "Жёстких дисков": ("list", "", 2, ""),
        "PoE-портов": ("range", "", 3, "шт"),
        "Разрешение записи": ("range", "", 4, "Мп"),
    },
}

YES, NO = "Да", "Нет"
# slug, name, section, brand, price, old price, label, in stock, quantity, recommended, features
PRODUCTS = [
    (
        "ip-dome-2",
        "IP-камера купольная 2 Мп (демо)",
        "ip",
        "lumera",
        450000,
        None,
        "",
        True,
        25,
        False,
        {
            "Тип корпуса": "Купольная",
            "Цвет": "Белый",
            "Уличная": NO,
            "ИК-подсветка": "20",
            "Разрешение": "2",
            "Объектив": "2.8 мм",
            "PoE": YES,
            "Wi-Fi": NO,
            "Микрофон": YES,
        },
    ),
    (
        "ip-dome-4",
        "IP-камера купольная 4 Мп (демо)",
        "ip",
        "lumera",
        620000,
        690000,
        "sale",
        True,
        7,
        True,
        {
            "Тип корпуса": "Купольная",
            "Цвет": "Белый",
            "Уличная": YES,
            "ИК-подсветка": "30",
            "Разрешение": "4",
            "Объектив": "2.8 мм",
            "PoE": YES,
            "Wi-Fi": NO,
            "Микрофон": YES,
        },
    ),
    (
        "ip-bullet-4",
        "IP-камера цилиндрическая 4 Мп (демо)",
        "ip",
        "ostrix",
        710000,
        None,
        "new",
        True,
        None,
        True,
        {
            "Тип корпуса": "Цилиндрическая",
            "Цвет": "Белый",
            "Уличная": YES,
            "ИК-подсветка": "40",
            "Разрешение": "4",
            "Объектив": "3.6 мм",
            "PoE": YES,
            "Wi-Fi": NO,
            "Микрофон": NO,
        },
    ),
    (
        "ip-bullet-8",
        "IP-камера цилиндрическая 8 Мп (демо)",
        "ip",
        "ostrix",
        1350000,
        None,
        "",
        False,
        None,
        False,
        {
            "Тип корпуса": "Цилиндрическая",
            "Цвет": "Черный",
            "Уличная": YES,
            "ИК-подсветка": "60",
            "Разрешение": "8",
            "Объектив": "2.8–12 мм",
            "PoE": YES,
            "Wi-Fi": NO,
            "Микрофон": NO,
        },
    ),
    (
        "ip-wifi-2",
        "Wi-Fi камера 2 Мп (демо)",
        "ip",
        "vigilo",
        380000,
        420000,
        "promo",
        True,
        3,
        False,
        {
            "Тип корпуса": "Купольная",
            "Цвет": "Белый",
            "Уличная": NO,
            "ИК-подсветка": "20",
            "Разрешение": "2",
            "Объектив": "3.6 мм",
            "PoE": NO,
            "Wi-Fi": YES,
            "Микрофон": YES,
        },
    ),
    (
        "ip-ptz-4",
        "Поворотная IP-камера 4 Мп (демо)",
        "ip",
        "vigilo",
        2900000,
        None,
        "new",
        True,
        2,
        True,
        {
            "Тип корпуса": "Поворотная",
            "Цвет": "Белый",
            "Уличная": YES,
            "ИК-подсветка": "60",
            "Разрешение": "4",
            "Объектив": "2.8–12 мм",
            "PoE": YES,
            "Wi-Fi": NO,
            "Микрофон": YES,
        },
    ),
    (
        "ip-wifi-4-black",
        "Wi-Fi камера уличная 4 Мп (демо)",
        "ip",
        "vigilo",
        560000,
        None,
        "",
        True,
        14,
        False,
        {
            "Тип корпуса": "Цилиндрическая",
            "Цвет": "Черный",
            "Уличная": YES,
            "ИК-подсветка": "30",
            "Разрешение": "4",
            "Объектив": "3.6 мм",
            "PoE": NO,
            "Wi-Fi": YES,
            "Микрофон": YES,
        },
    ),
    (
        "an-dome-2",
        "AHD-камера купольная 2 Мп (демо)",
        "an",
        "lumera",
        210000,
        None,
        "",
        True,
        40,
        False,
        {
            "Тип корпуса": "Купольная",
            "Цвет": "Белый",
            "Уличная": NO,
            "ИК-подсветка": "20",
            "Разрешение": "2",
            "Объектив": "2.8 мм",
            "Формат сигнала": "AHD",
        },
    ),
    (
        "an-bullet-5",
        "TVI-камера цилиндрическая 5 Мп (демо)",
        "an",
        "ostrix",
        340000,
        390000,
        "sale",
        True,
        6,
        False,
        {
            "Тип корпуса": "Цилиндрическая",
            "Цвет": "Белый",
            "Уличная": YES,
            "ИК-подсветка": "40",
            "Разрешение": "5",
            "Объектив": "3.6 мм",
            "Формат сигнала": "TVI",
        },
    ),
    (
        "an-bullet-2-black",
        "CVI-камера уличная 2 Мп (демо)",
        "an",
        "vigilo",
        260000,
        None,
        "",
        False,
        None,
        False,
        {
            "Тип корпуса": "Цилиндрическая",
            "Цвет": "Черный",
            "Уличная": YES,
            "ИК-подсветка": "30",
            "Разрешение": "2",
            "Объектив": "3.6 мм",
            "Формат сигнала": "CVI",
        },
    ),
    (
        "an-dome-5",
        "AHD-камера купольная 5 Мп (демо)",
        "an",
        "lumera",
        None,
        None,
        "new",
        True,
        None,
        False,
        {
            "Тип корпуса": "Купольная",
            "Цвет": "Черный",
            "Уличная": NO,
            "ИК-подсветка": "20",
            "Разрешение": "5",
            "Объектив": "2.8 мм",
            "Формат сигнала": "AHD",
        },
    ),
    (
        "nvr-4",
        "IP-видеорегистратор 4 канала (демо)",
        "nvr",
        "lumera",
        690000,
        None,
        "",
        True,
        9,
        True,
        {"Каналов": "4", "Жёстких дисков": "1", "PoE-портов": "4", "Разрешение записи": "8"},
    ),
    (
        "nvr-8",
        "IP-видеорегистратор 8 каналов (демо)",
        "nvr",
        "ostrix",
        1150000,
        1290000,
        "promo",
        True,
        4,
        False,
        {"Каналов": "8", "Жёстких дисков": "1", "PoE-портов": "8", "Разрешение записи": "8"},
    ),
    (
        "nvr-16",
        "IP-видеорегистратор 16 каналов (демо)",
        "nvr",
        "vigilo",
        2400000,
        None,
        "",
        True,
        None,
        False,
        {"Каналов": "16", "Жёстких дисков": "2", "PoE-портов": "0", "Разрешение записи": "12"},
    ),
    (
        "nvr-hybrid-8",
        "Гибридный видеорегистратор 8 каналов (демо)",
        "nvr",
        "lumera",
        980000,
        None,
        "new",
        False,
        None,
        False,
        {"Каналов": "8", "Жёстких дисков": "1", "PoE-портов": "0", "Разрешение записи": "5"},
    ),
]

# Cameras get recorders as related products and the other way round.
RELATED = {
    "ip-dome-4": ["nvr-4", "nvr-8"],
    "ip-bullet-4": ["nvr-8", "ip-dome-4"],
    "an-bullet-5": ["nvr-hybrid-8"],
    "nvr-8": ["ip-dome-4", "ip-bullet-4", "ip-wifi-2"],
}
WITH_DOCUMENTS = ["ip-dome-4", "ip-bullet-4", "nvr-8"]

DESCRIPTION = (
    "Демо-товар для проверки сайта: фильтров каталога, карточки и страницы товара.\n"
    "Название, цена и характеристики придуманы. Удалить все демо-товары: "
    "python manage.py demo_catalog --remove"
)


def demo_pdf(title: str) -> bytes:
    """A one-page PDF with a single line of text (Latin letters: no fonts to embed)."""
    stream = f"BT /F1 18 Tf 72 760 Td ({title}) Tj ET".encode()
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
        b"/Resources << /Font << /F1 5 0 R >> >> /Contents 4 0 R >>",
        b"<< /Length %d >>\nstream\n%s\nendstream" % (len(stream), stream),
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    ]
    out, offsets = b"%PDF-1.4\n", []
    for i, body in enumerate(objects, 1):
        offsets.append(len(out))
        out += b"%d 0 obj\n%s\nendobj\n" % (i, body)
    xref = len(out)
    out += b"xref\n0 %d\n0000000000 65535 f \n" % (len(objects) + 1)
    out += b"".join(b"%010d 00000 n \n" % o for o in offsets)
    out += b"trailer\n<< /Size %d /Root 1 0 R >>\nstartxref\n%d\n%%%%EOF\n" % (
        len(objects) + 1,
        xref,
    )
    return out


class Command(BaseCommand):
    help = "Create (or with --remove delete) the demo section «Видеонаблюдение (демо)»."

    def add_arguments(self, parser):
        parser.add_argument("--remove", action="store_true", help="delete the demo data")

    def handle(self, *args, **options):
        with transaction.atomic():
            if options["remove"]:
                self.remove()
                self.stdout.write("Демо-раздел удалён.")
                return
            count = self.create()
        self.stdout.write(f"Демо-раздел «{ROOT[1]}»: {count} товаров. Сайт: /catalog/{ROOT[0]}")

    def remove(self):
        demo = Product.objects.filter(slug__startswith="demo-")
        for doc in ProductDocument.objects.filter(product__in=demo):
            doc.delete()  # signals remove the file after the commit
        demo.delete()
        Category.objects.filter(slug__in=[s for s, _ in SUBS.values()]).delete()
        Category.objects.filter(slug=ROOT[0]).delete()
        Brand.objects.filter(slug__startswith="demo-").delete()

    def create(self) -> int:
        root, _ = Category.objects.update_or_create(slug=ROOT[0], defaults={"name": ROOT[1]})
        subs, values = {}, {}
        for key, (slug, name) in SUBS.items():
            subs[key], _ = Category.objects.update_or_create(
                slug=slug, defaults={"name": name, "parent": root}
            )
        brands = {
            key: Brand.objects.update_or_create(slug=f"demo-{key}", defaults={"name": name})[0]
            for key, name in BRANDS.items()
        }
        features = {}
        for key, spec in FEATURES.items():
            for name, (ftype, group, order, unit) in spec.items():
                features[key, name], _ = Feature.objects.update_or_create(
                    name=name,
                    category=subs[key],
                    defaults={"filter_type": ftype, "group": group, "order": order, "unit": unit},
                )

        products = {}
        for slug, name, sub, brand, price, old, label, avail, qty, rec, specs in PRODUCTS:
            p, _ = Product.objects.update_or_create(
                slug=f"demo-{slug}",
                defaults={
                    "name": name,
                    "category": subs[sub],
                    "brand": brands[brand],
                    "description": DESCRIPTION,
                    "price": None if price is None else Decimal(price),
                    "old_price": None if old is None else Decimal(old),
                    "status": label,
                    "is_available": avail,
                    "stock_quantity": qty,
                    "is_recommended": rec,
                },
            )
            p.features.all().delete()
            for fname, text in specs.items():
                key = (subs[sub].id, text)
                if key not in values:
                    values[key], _ = FeatureValue.objects.get_or_create(
                        category=subs[sub], value=text
                    )
                feature = features[sub, fname]
                feature.values.add(values[key])
                ProductFeature.objects.create(product=p, feature=feature, value=values[key])
            products[slug] = p

        for slug, others in RELATED.items():
            products[slug].related.set([products[o] for o in others])
        for slug in WITH_DOCUMENTS:
            p = products[slug]
            if not p.documents.exists():
                doc = ProductDocument(product=p, title="Паспорт изделия (демо)", order=0)
                doc.file.save(
                    f"demo-{slug}.pdf", ContentFile(demo_pdf("Demo passport")), save=False
                )
                doc.save()
        return len(products)
