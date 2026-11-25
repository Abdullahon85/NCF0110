"""Category tree helpers.

The tree is walked level by level (one query per level) with a visited set, so a
broken tree with a cycle (A -> B -> A) can never hang or crash a request.
"""
from typing import Iterable

from .models import Category


def subtree_ids(root_ids: Iterable[int]) -> list[int]:
    """The given categories plus all their descendants, each id once."""
    seen: list[int] = []
    visited: set[int] = set()
    level = [i for i in dict.fromkeys(root_ids) if i is not None]
    while level:
        level = [i for i in level if i not in visited]
        visited.update(level)
        seen.extend(level)
        if not level:
            break
        level = list(Category.objects.filter(parent_id__in=level).values_list("id", flat=True))
    return seen


def is_self_or_descendant(candidate_id: int, category_id: int) -> bool:
    """True when candidate_id is category_id itself or lies anywhere below it."""
    return candidate_id in subtree_ids([category_id])
