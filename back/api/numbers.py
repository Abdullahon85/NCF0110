"""The number inside a characteristic value ("10 000 000", "2,8 мм", "до 100"), for range filters."""

import re
from decimal import Decimal, InvalidOperation

# Optional minus, digits with optional thousands groups separated by (non-breaking) spaces,
# optional decimal part with a dot or a comma.
_NUMBER = re.compile(r"-?\d+(?:[   ]\d{3})*(?:[.,]\d+)?")


def parse_number(text: str | None) -> Decimal | None:
    """First number in the text, or None when there is none."""
    match = _NUMBER.search(text or "")
    if not match:
        return None
    raw = re.sub(r"[   ]", "", match.group()).replace(",", ".")
    try:
        return Decimal(raw)
    except InvalidOperation:
        return None
