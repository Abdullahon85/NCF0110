"""Discount shown next to a struck-through old price."""

from decimal import Decimal


def discount_percent(price: Decimal | None, old_price: Decimal | None) -> int | None:
    """Whole percent saved, only when old_price > price > 0; otherwise no discount."""
    if price is None or old_price is None or price <= 0 or old_price <= price:
        return None
    return int(((old_price - price) / old_price * 100).quantize(Decimal(1), "ROUND_HALF_UP"))
