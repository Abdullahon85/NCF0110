"""Catalog filtering for every product list (category, brand, search, promotions).

`GET /api/products/` and `GET /api/products/facets/` take the same query parameters:
    category=<slug>[,<slug>]   brand=a,b   status=new,promo   promo=1   recommended=1   ordered=1   in_stock=1
    price_min / price_max      q=<text>    sort=popular|price|-price|new|name   page, page_size
    f<facetId>=<valueId>,...   one list / yes-no characteristic: OR inside, AND between groups
    f<facetId>_min / _max      numeric range of a characteristic
Bad values are ignored, never an error. Characteristics with the same name and filter type in
the subcategories of the chosen category form ONE filter group whose id is the smallest
feature id ("Цвет" from three subcategories is one group, "Черный" one value with several ids).
Counts of a group are computed with every selected filter except the group's own (like shop.nag.uz).
"""

import re
from dataclasses import dataclass, field
from decimal import Decimal

from django.db.models import Count, F, Max, Min, Q, QuerySet, Sum
from django.db.models.functions import Coalesce

from .categories import subtree_ids
from .filters import parse_price
from .models import Category, Feature, OrderItem, Product, ProductFeature

SORTS = ("popular", "price", "-price", "new", "name")
PAGE_SIZES = (20, 40, 80)
MAX_FEATURE_GROUPS = 10  # each selected characteristic adds a subquery
_LIST_KEY = re.compile(r"^f(\d+)$")
_RANGE_KEY = re.compile(r"^f(\d+)_(min|max)$")
_TRUE = ("1", "true", "yes")


@dataclass
class FacetDef:
    id: int
    name: str
    group: str
    order: int
    type: str
    unit: str
    feature_ids: list[int] = field(default_factory=list)


@dataclass
class CatalogQuery:
    category: Category | None = None  # set only when exactly one category is chosen
    category_ids: list[int] | None = None  # whole subtree; None = no category filter
    brands: list[str] = field(default_factory=list)
    statuses: list[str] = field(default_factory=list)
    promo: bool = False
    recommended: bool = False
    ordered: bool = False  # only products that were ever ordered ("Популярное" on the home page)
    in_stock: bool = False
    price_min: Decimal | None = None
    price_max: Decimal | None = None
    lists: dict[int, list[int]] = field(default_factory=dict)
    ranges: dict[int, tuple[Decimal | None, Decimal | None]] = field(default_factory=dict)
    q: str = ""
    sort: str = "popular"


def _csv(params, name) -> list[str]:
    return [s.strip() for s in str(params.get(name) or "").split(",") if s.strip()]


def parse_catalog_query(params) -> CatalogQuery:
    query = CatalogQuery()
    slugs = _csv(params, "category")
    if slugs:
        cats = list(Category.objects.filter(slug__in=slugs))
        query.category_ids = subtree_ids([c.id for c in cats])
        query.category = cats[0] if len(cats) == 1 and len(slugs) == 1 else None
    query.brands = _csv(params, "brand")
    query.statuses = [s for s in _csv(params, "status") if s in Product.STATUS_LABELS]
    query.promo = str(params.get("promo", "")).lower() in _TRUE
    query.recommended = str(params.get("recommended", "")).lower() in _TRUE
    query.ordered = str(params.get("ordered", "")).lower() in _TRUE
    query.in_stock = str(params.get("in_stock", "")).lower() in _TRUE
    query.price_min = parse_price(params.get("price_min"))
    query.price_max = parse_price(params.get("price_max"))
    query.q = str(params.get("q") or params.get("search") or "").strip()
    sort = params.get("sort")
    query.sort = sort if sort in SORTS else "popular"

    for key in params:
        if len(query.lists) + len(query.ranges) >= MAX_FEATURE_GROUPS:
            break
        if m := _LIST_KEY.match(key):
            ids = [int(v) for v in _csv(params, key) if v.isdigit()]
            if ids:
                query.lists[int(m.group(1))] = ids
        elif m := _RANGE_KEY.match(key):
            value = parse_price(params.get(key))
            if value is not None:
                low, high = query.ranges.get(int(m.group(1)), (None, None))
                query.ranges[int(m.group(1))] = (
                    (value, high) if m.group(2) == "min" else (low, value)
                )
    return query


def page_size(params) -> int:
    raw = params.get("page_size")
    return int(raw) if raw and raw.isdigit() and int(raw) in PAGE_SIZES else PAGE_SIZES[0]


def facet_defs(category_ids: list[int] | None) -> list[FacetDef]:
    """Characteristics shown as filters, same-named ones merged; all of them without a category."""
    features = Feature.objects.exclude(filter_type="none").order_by("order", "name", "id")
    if category_ids is not None:
        features = features.filter(category_id__in=category_ids)
    defs: dict[tuple[str, str], FacetDef] = {}
    for f in features:
        key = (f.name.strip().lower(), f.filter_type)
        if key not in defs:
            defs[key] = FacetDef(f.id, f.name, f.group, f.order, f.filter_type, f.unit)
        defs[key].feature_ids.append(f.id)
        defs[key].id = min(defs[key].id, f.id)
    return list(defs.values())


def _with_values(qs: QuerySet, feature_ids: list[int], value_ids: list[int]) -> QuerySet:
    # The characteristic matters: one value row ("Да", "Черный") is shared by every
    # characteristic of the category, so PoE = Да must not match Wi-Fi = Да.
    links = ProductFeature.objects.filter(feature_id__in=feature_ids, value_id__in=value_ids)
    return qs.filter(id__in=links.values("product_id"))


def filter_products(query: CatalogQuery, skip: str | None = None, defs=None) -> QuerySet:
    """Products matching every selected filter except the group named by `skip`
    ("brand", "status", "price" or "f<facetId>")."""
    qs = Product.objects.all()
    if query.category_ids is not None:
        qs = qs.filter(category_id__in=query.category_ids)
    if query.brands and skip != "brand":
        qs = qs.filter(brand__slug__in=query.brands)
    if query.statuses and skip != "status":
        qs = qs.filter(status__in=query.statuses)
    if query.promo:
        qs = qs.filter(Q(status__in=("promo", "sale")) | Q(old_price__gt=F("price")))
    if query.recommended:
        qs = qs.filter(is_recommended=True)
    if query.ordered:
        qs = qs.filter(id__in=OrderItem.objects.values("product_id"))
    if query.in_stock:
        qs = qs.filter(is_available=True)
    if skip != "price":
        if query.price_min is not None:
            qs = qs.filter(price__gte=query.price_min)
        if query.price_max is not None:
            qs = qs.filter(price__lte=query.price_max)
    if query.q:
        qs = qs.filter(
            Q(name__icontains=query.q)
            | Q(description__icontains=query.q)
            | Q(manufacturer_sku__icontains=query.q)
            | Q(internal_sku__icontains=query.q)
        )
    by_id = {}
    if query.lists or query.ranges:
        by_id = {d.id: d for d in (defs if defs is not None else facet_defs(query.category_ids))}
    for facet_id, ids in query.lists.items():
        if skip != f"f{facet_id}":
            facet = by_id.get(facet_id)
            qs = _with_values(qs, facet.feature_ids if facet else [facet_id], ids)
    if query.ranges:
        for facet_id, (low, high) in query.ranges.items():
            if skip == f"f{facet_id}":
                continue
            facet = by_id.get(facet_id)
            links = ProductFeature.objects.filter(
                feature_id__in=facet.feature_ids if facet else [facet_id]
            )
            if low is not None:
                links = links.filter(value__number__gte=low)
            if high is not None:
                links = links.filter(value__number__lte=high)
            qs = qs.filter(id__in=links.values("product_id"))
    return qs


def sort_products(qs: QuerySet, sort: str) -> QuerySet:
    if sort == "price":
        return qs.order_by(F("price").asc(nulls_last=True), "-created_at", "-id")
    if sort == "-price":
        return qs.order_by(F("price").desc(nulls_last=True), "-created_at", "-id")
    if sort == "new":
        return qs.order_by("-created_at", "-id")
    if sort == "name":
        return qs.order_by("name", "id")
    return qs.annotate(popularity=Coalesce(Sum("order_items__quantity"), 0)).order_by(
        "-popularity", "-created_at", "-id"
    )


def _num(value) -> float | None:
    return float(value) if value is not None else None


def _value_sort_key(facet_type: str, text: str, number):
    if facet_type == "bool":
        return (0 if text.strip().lower() in ("да", "есть", "yes") else 1, text)
    return (number is None, number or 0, text.lower())


def build_facets(query: CatalogQuery) -> dict:
    defs = facet_defs(query.category_ids) if query.category_ids else []
    matching = filter_products(query, defs=defs)

    without_price = filter_products(query, "price", defs).exclude(price__isnull=True)
    prices = without_price.aggregate(min=Min("price"), max=Max("price"))

    categories = []
    if query.category is not None:
        for child in query.category.children.order_by("order", "name"):
            count = matching.filter(category_id__in=subtree_ids([child.id])).count()
            categories.append({"slug": child.slug, "name": child.name, "count": count})

    brand_rows = (
        filter_products(query, "brand", defs)
        .exclude(brand__isnull=True)
        .values("brand__slug", "brand__name")
        .annotate(count=Count("id", distinct=True))
    )
    brands = sorted(
        (
            {"slug": r["brand__slug"], "name": r["brand__name"], "count": r["count"]}
            for r in brand_rows
        ),
        key=lambda b: b["name"].lower(),
    )

    status_counts = dict(
        filter_products(query, "status", defs)
        .exclude(status="")
        .values_list("status")
        .annotate(count=Count("id", distinct=True))
    )
    statuses = [
        {"value": value, "label": label, "count": status_counts.get(value, 0)}
        for value, label in Product.STATUS_LABELS.items()
        if status_counts.get(value) or value in query.statuses
    ]

    features = []
    in_scope = ProductFeature.objects.filter(product__category_id__in=query.category_ids or [])
    for d in defs:
        base = filter_products(query, f"f{d.id}", defs)
        links = in_scope.filter(feature_id__in=d.feature_ids)
        if d.type == "range":
            bounds = links.filter(product__in=base, value__number__isnull=False).aggregate(
                min=Min("value__number"), max=Max("value__number")
            )
            if bounds["min"] is not None:
                features.append(
                    {
                        "id": d.id,
                        "name": d.name,
                        "group": d.group,
                        "type": "range",
                        "unit": d.unit,
                        "min": _num(bounds["min"]),
                        "max": _num(bounds["max"]),
                    }
                )
            continue
        values: dict[str, dict] = {}
        for value_id, text, number in links.values_list(
            "value_id", "value__value", "value__number"
        ).distinct():
            entry = values.setdefault(text.strip(), {"ids": set(), "number": number, "count": 0})
            entry["ids"].add(value_id)
        counts = (
            links.filter(product__in=base)
            .values("value__value")
            .annotate(count=Count("product_id", distinct=True))
        )
        for row in counts:
            if row["value__value"].strip() in values:
                values[row["value__value"].strip()]["count"] = row["count"]
        if values:
            ordered = sorted(
                values.items(), key=lambda kv: _value_sort_key(d.type, kv[0], kv[1]["number"])
            )
            features.append(
                {
                    "id": d.id,
                    "name": d.name,
                    "group": d.group,
                    "type": d.type,
                    "values": [
                        {"ids": sorted(v["ids"]), "value": text, "count": v["count"]}
                        for text, v in ordered
                    ],
                }
            )

    return {
        "total": matching.count(),
        "price": {"min": _num(prices["min"]), "max": _num(prices["max"])},
        "in_stock": matching.filter(is_available=True).count()
        if not query.in_stock
        else matching.count(),
        "categories": categories,
        "brands": brands,
        "statuses": statuses,
        "features": features,
    }
