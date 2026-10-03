"""Protection against CSV/formula injection in spreadsheet exports.

Excel/LibreOffice treat a cell starting with = + - @ (or a leading tab/CR)
as a formula. Customer-supplied text is prefixed with an apostrophe so it is
shown as text. Phone-number-like values (+998 90 123-45-67) are left as is.
"""
import re

_FORMULA_TRIGGERS = ("=", "+", "-", "@", "\t", "\r")
_PHONE_LIKE = re.compile(r"\+?[0-9][0-9 ()\-]*")


def safe_csv_cell(value: object) -> object:
    if not isinstance(value, str) or not value.startswith(_FORMULA_TRIGGERS):
        return value
    if _PHONE_LIKE.fullmatch(value):
        return value
    return "'" + value
