"""Data flow graph: def-use edges from a reaching-definitions analysis over the CFG."""


def def_use_edges(g):
    """Return (edges, free_vars) for a built CFG `g` (anything with .nodes and .edges).

    edges     sorted (def_node, use_node, var): the value of `var` defined at def_node may be
              read at use_node.
    free_vars sorted names read somewhere without any reaching definition (globals, builtins,
              fields, closure variables).
    """
    n = len(g.nodes)
    preds = [[] for _ in range(n)]
    for a, b, _ in g.edges:
        preds[b].append(a)
    gen = [{(v, i) for v in g.nodes[i]["defs"]} for i in range(n)]
    killed_vars = [set(g.nodes[i]["defs"]) for i in range(n)]
    IN = [set() for _ in range(n)]
    OUT = [set(gen[i]) for i in range(n)]
    changed = True
    while changed:
        changed = False
        for i in range(n):
            new_in = set().union(*(OUT[p] for p in preds[i])) if preds[i] else set()
            new_out = gen[i] | {(v, d) for (v, d) in new_in if v not in killed_vars[i]}
            if new_in != IN[i] or new_out != OUT[i]:
                IN[i], OUT[i] = new_in, new_out
                changed = True
    edges, free = set(), set()
    for i in range(n):
        for v in g.nodes[i]["uses"]:
            ds = [d for (vv, d) in IN[i] if vv == v]
            if not ds:
                free.add(v)
            for d in ds:
                edges.add((d, i, v))
    return sorted(edges), sorted(free)
