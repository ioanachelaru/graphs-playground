"""Small tree-sitter helpers shared by all language front-ends."""


def names(nodes) -> list:
    """Sorted, de-duplicated source text of identifier nodes."""
    return sorted({n.text.decode("utf8", "replace") for n in nodes})


def first_line(node, limit: int = 120) -> str:
    """First source line of a node, stripped and truncated (used as the CFG node label)."""
    s = node.text.decode("utf8", "replace").split("\n", 1)[0].strip()
    return s[:limit]


def count_errors(node) -> int:
    """Number of ERROR / MISSING nodes below `node` (0 when the subtree parsed cleanly)."""
    if not node.has_error:
        return 0
    k, stack = 0, [node]
    while stack:
        n = stack.pop()
        if n.type == "ERROR" or n.is_missing:
            k += 1
        elif n.has_error:
            stack.extend(n.children)
    return k
