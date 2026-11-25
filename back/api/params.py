"""Parsing of query parameters and inline admin input.

Bad values raise DRF ValidationError, which the API turns into a 400 with the
field name, instead of letting the database layer fail with a 500.
"""
from datetime import date
from decimal import Decimal, InvalidOperation

from rest_framework.exceptions import ValidationError


def int_param(params, name: str) -> int | None:
    raw = params.get(name)
    if raw is None or str(raw).strip() == "":
        return None
    try:
        return int(str(raw).strip())
    except ValueError:
        raise ValidationError({name: "Должно быть целое число."})


def date_param(params, name: str) -> date | None:
    raw = str(params.get(name) or "").strip()
    if not raw:
        return None
    try:
        return date.fromisoformat(raw)
    except ValueError:
        raise ValidationError({name: "Дата должна быть в формате ГГГГ-ММ-ДД."})


def inline_list(data, key: str) -> list[dict]:
    """data[key] as a list of objects ([] when absent or null)."""
    value = data.get(key)
    if value is None:
        return []
    if not isinstance(value, list) or not all(isinstance(item, dict) for item in value):
        raise ValidationError({key: "Ожидается список объектов."})
    return value


MAX_PRICE = Decimal(10) ** 23  # Product.price is DECIMAL(25, 2)


def price_value(data, name: str = "price") -> Decimal | None:
    """A price typed by the admin: empty -> None (no price), else a number from 0,
    below 10^23, with at most 2 decimals. Anything else would be stored by SQLite
    and then break every page that reads the product."""
    raw = data.get(name)
    if raw is None or str(raw).strip() == "":
        return None
    try:
        value = Decimal(str(raw).strip().replace(",", "."))
    except InvalidOperation:
        raise ValidationError({name: "Цена должна быть числом, например 1500000 или 99.50."})
    if not value.is_finite() or value < 0 or value >= MAX_PRICE:
        raise ValidationError({name: "Цена должна быть не меньше 0 и не больше 23 знаков."})
    if value.as_tuple().exponent < -2:
        raise ValidationError({name: "Не больше двух знаков после запятой."})
    return value
