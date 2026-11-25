"""URL slugs: always non-empty, ASCII, unique per model.

Django's slugify() drops Cyrillic letters, so a Russian name like "Камеры" used
to become an empty slug. Names are transliterated first (Russian and Uzbek
Cyrillic; apostrophes of Uzbek Latin such as O‘zbekiston are dropped).
Front/src/utils/slug.ts uses the same table: keep the two in sync.
"""
from django.utils.text import slugify

_CYRILLIC = {
    "а": "a", "б": "b", "в": "v", "г": "g", "д": "d", "е": "e", "ё": "yo",
    "ж": "zh", "з": "z", "и": "i", "й": "y", "к": "k", "л": "l", "м": "m",
    "н": "n", "о": "o", "п": "p", "р": "r", "с": "s", "т": "t", "у": "u",
    "ф": "f", "х": "h", "ц": "ts", "ч": "ch", "ш": "sh", "щ": "sch", "ъ": "",
    "ы": "y", "ь": "", "э": "e", "ю": "yu", "я": "ya",
    # Uzbek Cyrillic
    "ў": "o", "қ": "q", "ғ": "g", "ҳ": "h",
}
_APOSTROPHES = "'‘’ʻʼ`"

FALLBACK_SLUG = "item"


def transliterate(text: str) -> str:
    text = (text or "").lower()
    for mark in _APOSTROPHES:
        text = text.replace(mark, "")
    return "".join(_CYRILLIC.get(ch, ch) for ch in text)


def make_slug(text: str, max_length: int) -> str:
    slug = slugify(transliterate(text))[:max_length].strip("-")
    return slug or FALLBACK_SLUG


def unique_slug(model, text: str, max_length: int, exclude_pk=None) -> str:
    """make_slug(text), plus -2, -3, ... while another row of `model` already uses it."""
    base = make_slug(text, max_length)
    others = model.objects.exclude(pk=exclude_pk) if exclude_pk else model.objects.all()
    candidate, n = base, 2
    while others.filter(slug=candidate).exists():
        suffix = f"-{n}"
        candidate = base[: max_length - len(suffix)].rstrip("-") + suffix
        n += 1
    return candidate
