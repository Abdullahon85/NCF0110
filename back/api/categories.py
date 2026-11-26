"""Category tree helpers.

The tree is walked level by level (one query per level) with a visited set, so a
broken tree with a cycle (A -> B -> A) can never hang or crash a request.
"""

from collections.abc import Iterable

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


def category_ancestors(category) -> list[dict]:
    """Parents of a category from the root down; a broken tree with a cycle stops safely."""
    chain, seen, parent = [], {category.id}, category.parent
    while parent is not None and parent.id not in seen:
        seen.add(parent.id)
        chain.append({"name": parent.name, "slug": parent.slug})
        parent = parent.parent
    return chain[::-1]
