"""Validation of admin-entered links rendered into <a href> on the public site."""
import re
from urllib.parse import urlsplit

from rest_framework import serializers

SAFE_LINK_SCHEMES = {"", "http", "https", "mailto", "tel"}

# Browsers ignore whitespace and control characters inside a URL scheme
# ("java\tscript:" still runs), so they are removed before checking it.
_IGNORED_IN_SCHEME = re.compile(r"[\x00-\x20\x7f]")


def validate_safe_link(value: str | None) -> str | None:
    if not value:
        return value
    stripped = value.strip()
    scheme = urlsplit(_IGNORED_IN_SCHEME.sub("", stripped)).scheme.lower()
    if scheme not in SAFE_LINK_SCHEMES:
        raise serializers.ValidationError(
            "Ссылка должна начинаться с http://, https:// или быть относительной (например /catalog)."
        )
    return stripped
