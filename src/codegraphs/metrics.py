"""Per-function graph metrics (one row of metrics.csv).

Column order: loc, cfg_nodes, cfg_edges, cyclomatic, <language-specific node-kind counts>,
max_depth, dfg_edges, n_defs, n_uses, n_vars, n_free_vars, n_params, has_parse_error.
The node-kind counts come from `Language.kind_counts`: (column, node kinds summed) pairs.
"""


def compute(g, dfg, free, fn, start, kind_counts) -> dict:
    kinds = [x["kind"] for x in g.nodes]
    n_nodes, n_edges = len(g.nodes), len(g.edges)
    row = {
        "loc": fn.end_point[0] - start.start_point[0] + 1,
        "cfg_nodes": n_nodes,
        "cfg_edges": n_edges,
        "cyclomatic": n_edges - n_nodes + 2,
    }
    for col, ks in kind_counts:
        row[col] = sum(kinds.count(k) for k in ks)
    row.update({
        "max_depth": max(x["depth"] for x in g.nodes),
        "dfg_edges": len(dfg),
        "n_defs": sum(len(x["defs"]) for x in g.nodes),
        "n_uses": sum(len(x["uses"]) for x in g.nodes),
        "n_vars": len({v for x in g.nodes for v in x["defs"]}),
        "n_free_vars": len(free),
        "n_params": len(g.nodes[0]["defs"]),
        "has_parse_error": int(fn.has_error),
    })
    return row
